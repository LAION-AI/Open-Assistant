import os
import signal
import sys
from pathlib import Path

import huggingface_hub


def terminate(signum, frame):
    print("Terminating...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, terminate)
    model_id = os.getenv("MODEL_ID")
    snapshot_dir = Path(huggingface_hub.snapshot_download(model_id))
    for file in snapshot_dir.rglob("*.json"):
        text = file.read_text()
        text = text.replace("LLaMA", "Llama")
        file.write_text(text)
