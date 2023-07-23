import torch
from model_training.models.patching import patch_model
from transformers import AutoModelForCausalLM, AutoTokenizer


def test_flash_attention_patch(dtype=torch.float16, device="cuda:0", llama_path="/mnt/data/llama2/Llama-2-7b"):
    tokenizer = AutoTokenizer.from_pretrained(llama_path)
    tokenizer.add_special_tokens({"pad_token": "</s>", "eos_token": "</s>", "sep_token": "<s>"})

    model = AutoModelForCausalLM.from_pretrained(llama_path, torch_dtype=dtype).to(device)
    patched_model = AutoModelForCausalLM.from_pretrained(llama_path, torch_dtype=dtype).to(device)
    patch_model(patched_model, resid_pdrop=None, flash_attention=True)

    device = model.device
    n_heads = model.config.num_attention_heads
    head_dim = model.config.hidden_size // n_heads

    with torch.no_grad():
        for layer1, layer2 in zip(model.model.layers, patched_model.model.layers):
            hidden_states = torch.randn(4, 10, head_dim * n_heads, dtype=dtype, device=device)
            attention_mask = (torch.randn(4, 10, device=device).sort(dim=-1).values < 0.5).int()
            attn_mask = patched_model.model._prepare_decoder_attention_mask(attention_mask, (4, 10), hidden_states, 0)
            position_ids = torch.arange(10, device=device).unsqueeze(0).expand(4, -1)
            attn1, attn2 = layer1.self_attn, layer2.self_attn

            out1, _, _ = attn1(hidden_states, attention_mask=attn_mask, position_ids=position_ids)
            out2, _, _ = attn2(hidden_states, attention_mask=attn_mask, position_ids=position_ids)

            assert (((out1 - out2) * attention_mask.unsqueeze(-1)).mean(dim=-1).abs() < 1e-3).all()

        batch = tokenizer(["hello world", "lorem ipsum dolor sit amet"], padding=True, return_tensors="pt").to(device)
        out1 = model(**batch).logits
        out2 = patched_model(**batch).logits

        diff = (out1 - out2) * batch["attention_mask"].unsqueeze(-1)
        assert (diff.abs() < 0.1).all()

    input_ids = torch.randint(0, model.config.vocab_size, size=(2, 10), device=device)
    patched_model(input_ids).logits.mean().backward()


if __name__ == "__main__":
    test_flash_attention_patch()
