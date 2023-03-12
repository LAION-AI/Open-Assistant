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

## Development Variant 2 (tmux terminal multiplexing)

Ensure you have `tmux` installed on you machine and the following packages
installed into the Python environment;

- `uvicorn`
- `worker/requirements.txt`
- `server/requirements.txt`
- `text-client/requirements.txt`
- `oasst_shared`

You can run development setup to start the full development setup.

```bash
cd inference
./full-dev-setup.sh
```

> Make sure to wait until the 2nd terminal is ready and says
> `{"message":"Connected"}` before entering input into the last terminal.

## Development Variant 3 (you'll need multiple terminals)

Run a postgres container:

```bash
docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name postgres postgres
```

Run a redis container (or use the one of the general docker compose file):

```bash
docker run --rm -it -p 6379:6379 redis
```

Run the inference server:

```bash
cd server
pip install -r requirements.txt
DEBUG_API_KEYS='["0000"]' uvicorn main:app --reload
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

Run the text client:

```bash
cd text-client
pip install -r requirements.txt
python __main__.py
```

## Inference Flow

1. client authenticates

2. client makes a POST request to /chat

3. /chat creates a ChatRepository() and gets all chats


---
title: Node with text
--- 




client_handler

OASST_INFERENCE_SERVER

- worker_handler.handle_worker (websocket passed here)
- client_handler.handle_create_message
- deps: fastapi dependency injection system (lots of factory functions)
- interface: 
- chatrepository: class which acts as an interface between application
logic and chats and messages tables.

use websockets for client-server chat (need 2-way messages for chat).

for server to fastapi backend, use Server Sent Events (1-way). websocket would require too
many heavy gpu resources.

websocket can use async io to send and receive messages in background without blocking thread.

review async:
async
await

continue -> worker_handler.handle_worker()

we parse the websocket text to create the worker config. the worker config includes:
- model_name
- hardware_info

none of this is actually in the websocket text and is in fact created from 
default factories, but potentially websocket text could pass additional information
pynvml is used to get information about the literal gpu hardware on the server.

next, a worker compatability "hash" is created, although this hash is just the model
name.

next a worker queue is created which is really just a redis queue. 

next a redis_client is created.

next a uuid4 worker session id is created

next we create a db session and add the worker connect event

then we set in redis the worker_session_id and the worker config

then enter a while loop where:
- we check to see if client is disconnected: if so raise
- we do compliance checks
- we try to dequeue any work which has been done
- if there is nothing in the done work queue, we continue to next loop
  iteration.
- if there is something in the queue we call perform work

in perform work,
we connect to the message table (using ChatRepository) and get
the message content using message id, we also update the message
table entry with the time of the work, the worker id, the model compat hash (model name)
and worker config

next we make a work request:
in a work request, we get the chat of the messages,
we create a dictionary of all messages
and then we create a list of all messages, aka a "thread"

finally, we return a WorkRequest which includes this thread, a created at datetime and 
a parameters attribute, which is connected to the message entry and set by a default factory which points to a pydantic class, `WorkParameters`. `WorkParameters` includes:
- model_name
- max_new_tokens = 100
- do_sample = True
- top_k = 50
- top_p = 0.9
- temperature = 1.0
- repetition_penalty = float | None
- seed

we are then back in `perform_work` where we send the work request via websocket

then we get the generated response as part of the 
response_packet = receive_work_response_packet(websocket)

then we send a work request with a websocket. this goes back to user. why do we send this?

how does a message get sent to a worker?

inference.WorkResponsePacket