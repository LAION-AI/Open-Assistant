import os
import signal
import sys

import transformers


def terminate(signum, frame):
    print("Terminating...")
    sys.exit(__status=0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, terminate)
    model_id = os.getenv(key="MODEL_ID")
    if "llama" in model_id.lower():
        transformers.LlamaTokenizer.from_pretrained(pretrained_model_name_or_path=model_id)
        transformers.LlamaForCausalLM.from_pretrained(pretrained_model_name_or_path=model_id)
    else:
        transformers.AutoTokenizer.from_pretrained(pretrained_model_name_or_path=model_id)
        transformers.AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=model_id)
