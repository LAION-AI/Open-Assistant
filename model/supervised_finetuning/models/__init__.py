from transformers import AutoModelForCausalLM

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


def get_specific_model(model_name, cache_dir, quantization):
    return AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
    # if "gpt-j" in model_name.lower():
    #     return get_gptj_model(model_name, cache_dir, quantization)
    # else:
    #     return AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
