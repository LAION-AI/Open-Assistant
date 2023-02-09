# OpenAssistant Inference

Preliminary implementation of the inference engine for OpenAssistant.

## Development Variant 1 (docker compose)

The services of the inference stack are prefixed with "inference-" in the
[unified compose descriptor](../docker-compose.yaml). <br/> Prior to building
those, please ensure that you have Docker's new
[BuildKit](https://docs.docker.com/build/buildkit/) backend enabled. See the
[FAQ](https://projects.laion.ai/Open-Assistant/docs/faq#enable-dockers-buildkit-backend)
for more info.

To build the services, run:

```shell
docker compose --profile inference build
```

Spin up the stack:

```shell
docker compose --profile inference up -d
```

Tail the logs:

```shell
docker compose logs -f    \
    inference-server      \
    inference-worker      \
    inference-text-client \
    inference-text-generation-server
```

Attach to the text-client, and start chatting:

```shell
docker attach open-assistant-inference-text-client-1
```

> **Note:** In the last step, `open-assistant-inference-text-client-1` refers to
> the name of the `text-client` container started in step 2.

> **Note:** The compose file contains the bind mounts enabling you to develop on
> the modules of the inference stack, and the `oasst-shared` package, without
> rebuilding.

> **Note:** You can spin up any number of workers by adjusting the number of
> replicas of the `inference-worker` service to your liking.

> **Note:** Please wait for the `inference-text-generation-server` service to
> output `{"message":"Connected"}` before starting to chat.

## Development Variant 2 (you'll need tmux)

Run `./full-dev-setup.sh` to start the full development setup. Make sure to wait
until the 2nd terminal is ready and says `{"message":"Connected"}` before
entering input into the last terminal.

## Development Variant 3 (you'll need multiple terminals)

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
docker run --rm -it -p 8001:80 -e MODEL_ID=distilgpt2 ghcr.io/huggingface/text-generation-inference
```

Run the client:

```bash
cd text-client
pip install -r requirements.txt
python __main__.py
```
