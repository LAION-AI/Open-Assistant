import json
import time

import redis
import typer
from transformers import pipeline

app = typer.Typer()


@app.command()
def main(model_name: str = "distilgpt2", redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
    pipe = pipeline("text-generation", model=model_name)

    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    work_queue_name = f"work-{model_name}"

    while True:
        item = redis_client.brpop(work_queue_name)
        if item is None:
            continue
        _, work_str = item
        work = json.loads(work_str)
        queue_id = work["queue_id"]
        text = work["text"]
        print(f"Processing {queue_id} {len(text)=}...")

        # TODO: replace this with incremental generation
        model_output = pipe(text, max_length=50, do_sample=True, return_full_text=False)[0]["generated_text"]
        for word in model_output.split():
            redis_client.rpush(queue_id, word + " ")
            time.sleep(0.1)
        redis_client.rpush(queue_id, "<END>")


if __name__ == "__main__":
    app()
