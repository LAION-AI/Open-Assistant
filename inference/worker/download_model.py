import os
import signal
import sys
import concurrent.futures
import transformers


def download_model(model_id):
    if "llama" in model_id.lower():
        transformers.LlamaTokenizer.from_pretrained(model_id)
        transformers.LlamaForCausalLM.from_pretrained(model_id)
    else:
        transformers.AutoTokenizer.from_pretrained(model_id)
        transformers.AutoModelForCausalLM.from_pretrained(model_id)


def terminate(signum, frame):
    print("Terminating...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, terminate)
    model_ids = os.getenv("MODEL_IDS").split(",")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_model, model_id) for model_id in model_ids]
        concurrent.futures.wait(futures)
