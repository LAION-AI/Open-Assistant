import os
import signal
import sys

import transformers


def terminate(signum, frame):
    print("Terminating...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, terminate)
    model_id = os.getenv("MODEL_ID")
    if "llama" in model_id.lower():
        transformers.LlamaTokenizer.from_pretrained(model_id)
        transformers.LlamaForCausalLM.from_pretrained(model_id)
    else:
        transformers.AutoTokenizer.from_pretrained(model_id)
        transformers.AutoModelForCausalLM.from_pretrained(model_id)
