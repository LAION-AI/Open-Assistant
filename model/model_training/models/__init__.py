import transformers

# from .gptj import get_model as get_gptj_model

SUPPORTED_MODELS = ["galactica", "gpt-j"]


def freeze_top_n_layers(model, target_layers):
    # its possible we can simply detect which module is a ModuleList
    # and simply freeze the module without doing string parsing
    for name, param in model.named_parameters():
        if "embed" in name:
            param.requires_grad = False
        elif ".layer" in name or ".h." in name:
            tokens = name.split(".")
            layer_ = None
            for token in tokens:
                if token.isdigit():
                    layer_ = int(token)
                    break

            if layer_ is not None and layer_ < target_layers:
                # print('freeze ', layer_, name)
                param.requires_grad = False
    return model


def get_specific_model(model_name, seq2seqmodel=False, cache_dir=".cache", quantization=False, **kwargs):
    # encoder-decoder support for Flan-T5 like models
    # for now, we can use an argument but in the future,
    # we can automate this
    if seq2seqmodel:
        model = transformers.AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=cache_dir, **kwargs)
    else:
        model = transformers.AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir, **kwargs)
    return model
