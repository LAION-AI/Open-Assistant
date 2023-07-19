import torch
from model_training.models.patching import patch_model
from transformers import AutoTokenizer
from transformers.models.falcon.modeling_falcon import FalconForCausalLM


def test_flash_attention_falcon_patch(device="cuda:0"):
    model_name = "tiiuae/falcon-7b"
    dtype = torch.bfloat16

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    model = FalconForCausalLM.from_pretrained(model_name, torch_dtype=dtype).to(device)
    patched_model = FalconForCausalLM.from_pretrained(model_name, torch_dtype=dtype).to(device)
    patch_model(patched_model, resid_pdrop=None, flash_attention=True)

    with torch.no_grad():
        batch = tokenizer(["hello world", "lorem ipsum dolor sit amet"], padding=True, return_tensors="pt")
        batch = {k: v.to(device) for k, v in batch.items() if k != "token_type_ids"}

        out1 = model(use_cache=False, **batch).logits
        out2 = patched_model(use_cache=False, **batch).logits

        diff = (out1 - out2) * batch["attention_mask"].unsqueeze(-1)

        assert (diff.abs() < 0.3).all()

    input_ids = torch.randint(0, patched_model.config.vocab_size, size=(2, 10), device=device)
    patched_model(input_ids).logits.mean().backward()


if __name__ == "__main__":
    test_flash_attention_falcon_patch()
