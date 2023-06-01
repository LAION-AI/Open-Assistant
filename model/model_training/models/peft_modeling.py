from dataclasses import dataclass
from pathlib import Path

import torch
from huggingface_hub import hf_hub_download
from model_training.utils.utils import get_model, get_tokenizer
from peft import LoraConfig, PeftModel, PrefixTuningConfig, get_peft_model, prepare_model_for_int8_training

def transfer_embeddings(model,embed_path,tokenizer):
    old_embeddings = model.get_input_embeddings()
    old_num_tokens, old_embedding_dim = old_embeddings.weight.size()
    new_embeddings = torch.nn.Embedding(old_num_tokens, old_embedding_dim)
    new_embeddings.to(old_embeddings.weight.device, dtype=old_embeddings.weight.dtype)
    model._init_weights(new_embeddings)
    embed_weights = torch.load(embed_path,map_location=old_embeddings.weight.device)
    vocab_size = tokenizer.vocab_size
    new_embeddings.weight.data[:vocab_size, :] = old_embeddings.weight.data[:vocab_size, :]
    new_embeddings.weight.data[vocab_size:vocab_size + embed_weights.shape[0], :] = embed_weights.weight.data.to(
        new_embeddings.weight.dtype).to(new_embeddings.weight.device)
    model.set_input_embeddings(new_embeddings)
    model.tie_weights()

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
    extra_embeds = hf_hub_download(peft_model_path, "extra_embeddings.pt")
    transfer_embeddings(model,peft_model_path.joinpath('extra_embeddings.pt'),tokenizer)
    return model

def load_peft_finetuned_model(model,peft_model_path,tokenizer):
    transfer_embeddings(model,peft_model_path.joinpath('extra_embeddings.pt'),tokenizer)
    adapters_weights = torch.load(Path(peft_model_path).joinpath('adapter_model.bin'),map_location=model.device)
    model.load_state_dict(adapters_weights, strict=False)
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


def peft_model(model, model_name, peft_type="lora", int8_training=False, gradient_checkpointing=False):
    if peft_type == "lora":
        if "falcon" in model_name:
            target_modules = ["dense_4h_to_h", "dense", "query_key_value", "dense_h_to_4h"]
            r = 64
        elif "llama" in model_name:
            target_modules = ['down_proj', 'k_proj', 'q_proj', 'gate_proj', 'o_proj', 'up_proj', 'v_proj']
            if '65' in model_name:
                r = 16
            else:
                r = 64
        else:
            raise ValueError(f"Invalid model name '{model_name}'. The model name should contain 'falcon' or 'llama', Simply find target_modules for it")
        config = LoraConfig(
            r=r,
            lora_alpha=16,
            target_modules=target_modules,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
    elif peft_type == "prefix-tuning":
        config = PrefixTuningConfig(
            num_virtual_tokens=30, prefix_projection=True, encoder_hidden_size=1024, task_type="CAUSAL_LM"
        )
    else:
        raise ValueError("peft_method config is lora or prefix-tuning")
    model = get_peft_model(model, config)
    if int8_training:
        model = prepare_model_for_int8_training(model)

    if gradient_checkpointing:
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
    residual_dropout_lima: float = 0.3
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
    print(f"Vocab size is {vocab_size}, and new tokenizer length is {len(tokenizer)}")
    old_embeddings = model.get_input_embeddings()
    #todo saving more embedding than necessary, (pad embeds as well)
    new_embs = old_embeddings.weight.data[vocab_size :, :].clone()
    new_embs = new_embs.to(save_config.dtype)
    model.save_pretrained(save_config.adapter_save_path, torch_dtype=save_config.dtype)
    tokenizer.save_pretrained(save_config.adapter_save_path)
    torch.save(new_embs, Path(save_config.adapter_save_path).joinpath("extra_embeddings.pt"))
