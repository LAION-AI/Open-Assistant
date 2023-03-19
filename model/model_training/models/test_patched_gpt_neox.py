import torch
from patching import patch_model
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTNeoXModel


def test_flash_attention_patch(dtype=torch.float16, device="cuda"):
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m-deduped")
    tokenizer.add_special_tokens({"pad_token": "<pad>"})

    model = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-70m-deduped", torch_dtype=dtype).to(device)
    patched_model = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-70m-deduped", torch_dtype=dtype).to(device)
    patch_model(patched_model, resid_pdrop=None, flash_attention=True)

    device = model.device
    n_heads = model.config.num_attention_heads
    head_dim = model.config.hidden_size // n_heads

    with torch.no_grad():
        for layer1, layer2 in zip(model.gpt_neox.layers, patched_model.gpt_neox.layers):
            q = torch.randn(4, n_heads, 10, head_dim, dtype=dtype, device=device)
            k = torch.randn(4, n_heads, 10, head_dim, dtype=dtype, device=device)
            v = torch.randn(4, n_heads, 10, head_dim, dtype=dtype, device=device)
            attn1, attn2 = layer1.attention, layer2.attention

            out1, _ = attn1._attn(q, k, v)
            out2, _ = attn2._attn(q, k, v)

            assert ((out1 - out2).abs() < 1e-2).all()

        batch = tokenizer(["hello world", "lorem ipsum dolor sit amet"], padding=True, return_tensors="pt").to(device)
        out1 = model(**batch).logits
        out2 = patched_model(**batch).logits

        diff = (out1 - out2) * batch["attention_mask"].unsqueeze(-1)
        assert (diff.abs() < 1).all()

    input_ids = torch.randint(0, model.config.vocab_size, size=(2, 10), device=device)
    patched_model(input_ids).logits.mean().backward()


def test_resid_dropout_patch():
    model = GPTNeoXModel.from_pretrained("EleutherAI/pythia-70m-deduped")
    model.eval()

    with torch.no_grad():
        input_ids = torch.randint(0, 100, size=(2, 10))
        attention_mask = torch.ones_like(input_ids)

        logits_before = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state

        patch_model(model, resid_pdrop=0.2, flash_attention=False)

        logits_after = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state

        assert (
            logits_before - logits_after
        ).abs().sum() < 1e-5, "output is different before/after patching in eval mode"

        model.train()

        logits1 = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        logits2 = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state

        assert (logits1 - logits2).abs().sum() > 1e-5, "output is the same for different forward passes"

        x = model.get_input_embeddings()(input_ids)
        for layer in model.layers:
            y1 = layer.attention(x, None)[0]
            y2 = layer.attention(x, None)[0]
            assert (y1 - y2).abs().sum() > 1e-5, "attention output is the same for different forward passes"

            y1 = layer.mlp(x)
            y2 = layer.mlp(x)
            assert (y1 - y2).abs().sum() > 1e-5, "mlp output is the same for different forward passes"

    model = GPTNeoXModel.from_pretrained("EleutherAI/pythia-70m-deduped")
    patch_model(model, resid_pdrop=0.0, flash_attention=False)

    with torch.no_grad():
        logits1 = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        logits2 = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        assert (logits1 - logits2).abs().sum() < 1e-5, "output is the different for resid_pdrop=0"

    try:
        logits = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        logits.mean().backward()
    except Exception as e:
        raise Exception("patched backward pass failed") from e


if __name__ == "__main__":
    test_flash_attention_patch()
    test_resid_dropout_patch()
