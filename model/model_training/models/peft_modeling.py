from dataclasses import dataclass
from pathlib import Path

import torch
from huggingface_hub import hf_hub_download
from model_training.utils.utils import get_all_linear_layers, get_model, get_tokenizer, merge_dicts
from peft import LoraConfig, PeftModel, PrefixTuningConfig, get_peft_model, prepare_model_for_int8_training


def load_peft_model(model, peft_model_path, tokenizer):
    model.resize_token_embeddings(len(tokenizer))
    model.config.eos_token_id = tokenizer.eos_token_id
    model.config.bos_token_id = tokenizer.bos_token_id
    model.config.pad_token_id = tokenizer.pad_token_id
    model = PeftModel.from_pretrained(
        model,
        peft_model_path,
        torch_dtype=model.dtype,
    )
    model.eos_token_id = tokenizer.eos_token_id
    try:
        extra_embeds = hf_hub_download(peft_model_path, "extra_embeddings.pt")
        embed_weights = torch.load(extra_embeds, map_location=model.device)
        model.base_model.model.model.embed_tokens.weight[
            len(tokenizer) - embed_weights.shape[0] :, :
        ] = embed_weights.to(model.base_model.model.model.embed_tokens.weight.dtype)
    except Exception:
        print("Warning:Extra embeddings not added. This is expected if adapter file contains WTE")

    return model


def prepare_model_for_gradient_checkpointing(model):
    r"""
    Prepares the model for gradient checkpointing if necessary
    """
    if not getattr(model, "is_loaded_in_8bit", False):
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
        else:

            def make_inputs_require_grad(module, input, output):
                output.requires_grad_(True)

            model.get_input_embeddings().register_forward_hook(make_inputs_require_grad)
    return model


def peft_model(model, training_config):
    peft_config = training_config.peft_config
    peft_type = peft_config.pop("peft_type", "lora")
    if peft_type == "lora":
        default_args = {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": "all",
            "lora_dropout": 0.05,
            "bias": "none",
            "task_type": "CAUSAL_LM",
            "modules_to_save": ["wte", "lm_head"],
        }
        kwargs = merge_dicts(default_args, peft_config)
        if kwargs.get("target_modules") == "all":
            kwargs.update({"target_modules": get_all_linear_layers(model)})
        config = LoraConfig(**kwargs)
    elif peft_type == "prefix-tuning":
        default_args = {
            "num_virtual_tokens": 30,
            "prefix_projection": True,
            "encoder_hidden_size": 1024,
            "task_type": "CAUSAL_LM",
        }
        kwargs = merge_dicts(default_args, peft_config)
        config = PrefixTuningConfig(**kwargs)
    else:
        raise ValueError("peft_method config is lora or prefix-tuning")
    model = get_peft_model(model, config)

    if training_config.int8_training:
        model = prepare_model_for_int8_training(model)

    if training_config.gradient_checkpointing:
        model = prepare_model_for_gradient_checkpointing(model)
    model.print_trainable_parameters()
    return model


@dataclass
class SaveLoraConfig:
    dtype: torch.dtype = torch.float16
    is_reward_model: bool = False
    quantization: bool = False
    seq2seqmodel: bool = False
    freeze_layer: bool = False
    residual_dropout: float = 0
    use_flash_attention: bool = False
    adapter_save_path: str = "adapter"
    cache_dir: str = ""
    model_name: str = ""
    torch_ckpt_path: str = ""
    peft_type: str = "lora"


def save_adapter_model_from_ckpt(save_config: SaveLoraConfig):
    tokenizer = get_tokenizer(save_config)
    model = get_model(save_config, tokenizer)
    model = peft_model(model)
    model.load_state_dict(torch.load(save_config.torch_ckpt_path))
    vocab_size = tokenizer.vocab_size
    num_special_tokens = len(tokenizer.additional_special_tokens)

    new_embs = model.state_dict()["base_model.model.model.embed_tokens.weight"][
        vocab_size : vocab_size + num_special_tokens, :
    ].clone()
    new_embs = new_embs.to(save_config.dtype)
    model.save_pretrained(save_config.adapter_save_path, torch_dtype=save_config.dtype)
    tokenizer.save_pretrained(save_config.adapter_save_path)
    torch.save(new_embs, Path(save_config.adapter_save_path).joinpath("extra_embeddings.pt"))
