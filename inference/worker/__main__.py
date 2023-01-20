import re
import time

import redis
import requests
import torch
import typer
from loguru import logger
from oasst_shared.schemas import inference
from transformers import pipeline

app = typer.Typer()


@app.command()
def main(
    model_name: str = "distilgpt2",
    backend_url: str = "http://localhost:8000",
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
):

    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    worker_config = inference.WorkerConfig(model_name=model_name)

    pipe = pipeline("text-generation", model=model_name)

    # TODO: use batching
    while True:

        # wait for work to be ready
        # could possibly be switched to a message queue
        while True:
            try:
                response = requests.post(f"{backend_url}/work", json={"worker_config": worker_config.dict()})
                if response.status_code == 200:
                    break
            except Exception:
                logger.exception("Error connecting to backend")
            time.sleep(1)

        try:
            work_request = inference.WorkRequest.parse_raw(response.content)
            print(f"Processing {work_request}")
            queue_id = work_request.stream_queue_id

            # TODO: replace this with incremental generation
            torch.manual_seed(work_request.seed)
            model_output = pipe(
                work_request.prompt, max_length=work_request.max_length, do_sample=True, return_full_text=False
            )[0]["generated_text"]
            model_output = model_output.strip()

            # fake streaming
            split_idcs = [m.start() for m in re.finditer(r"(\w+)", model_output)]
            pieces = [model_output[a:b] for a, b in zip([0] + split_idcs, split_idcs + [None])]
            for piece in pieces:
                if not piece:
                    continue
                redis_client.rpush(queue_id, inference.WorkResponsePacket(token=piece).json())
                time.sleep(0.1)
            redis_client.rpush(queue_id, inference.WorkResponsePacket(is_end=True).json())
        except Exception:
            logger.exception(f"Error processing {work_request}")


if __name__ == "__main__":
    app()
