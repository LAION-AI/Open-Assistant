import os

import transformers

if __name__ == "__main__":
    model_id = os.getenv("MODEL_ID")
    if "llama" in model_id:
        transformers.LlamaTokenizer.from_pretrained(model_id)
        transformers.LlamaForCausalLM.from_pretrained(model_id)
    else:
        transformers.AutoTokenizer.from_pretrained(model_id)
        transformers.AutoModelForCausalLM.from_pretrained(model_id)
