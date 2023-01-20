# OpenAssitant Inference

Preliminary implementation of the inference engine for OpenAssistant.

## Development (you'll need multiple terminals)

Run a redis container:

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

Run the client:

```bash
cd text-client
pip install -r requirements.txt
python __main__.py
```
