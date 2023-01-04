from transformers import AutoModelForCausalLM
from .gptj import get_model as get_gptj_model

def get_specific_model(model_name, cache_dir, quantization):
    if "gpt-j" in model_name.lower():
        return get_gptj_model(model_name, cache_dir, quantization)
    else:
        return AutoModelForCausalLM.from_pretrained(conf.model_name, cache_dir=conf.cache_dir)