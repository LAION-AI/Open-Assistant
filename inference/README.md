# OpenAssitant Inference

Preliminary implementation of the inference engine for OpenAssistant.

## Development (you'll need multiple terminals)

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
