# OpenAssitant Inference

Preliminary implementation of the inference engine for OpenAssistant.

## Development Variant 1 (you'll need tmux)

Run `./full-dev-setup.sh` to start the full development setup. Make sure to wait
until the 2nd terminal is ready and says `{"message":"Connected"}` before
entering input into the last terminal.

## Development Variant 2 (you'll need multiple terminals)

Run a redis container (or use the one of the general docker compose file):

```bash
docker run --rm -it -p 6379:6379 redis
```

Run the inference server:

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

Run one (or more) workers:

```bash
cd worker
pip install -r requirements.txt
python __main__.py
```

For the worker, you'll also want to have the text-generation-inference server
running:

```bash
docker run --rm -it -p 8001:80 -e MODEL_ID=distilgpt2 ykilcher/text-generation-inference
```

Run the client:

```bash
cd text-client
pip install -r requirements.txt
python __main__.py
```
