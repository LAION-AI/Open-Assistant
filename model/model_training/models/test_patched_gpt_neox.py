import torch
from patch_resid_dropout import patch_model
from transformers import GPTNeoXModel


def main():
    model = GPTNeoXModel.from_pretrained("EleutherAI/pythia-70m-deduped")
    model.eval()

    with torch.no_grad():
        input_ids = torch.randint(0, 100, size=(2, 10))
        attention_mask = torch.ones_like(input_ids)

        logits_before = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state

        patch_model(model, resid_pdrop=0.2)

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
    patch_model(model, resid_pdrop=0.0)

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
    main()
