<a href="https://github-com.translate.goog/LAION-AI/Open-Assistant/blob/main/inference/README.md?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp">![Translate](https://img.shields.io/badge/Translate-blue)</a>

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
    inference-worker      

```

> **Note:** The compose file contains the bind mounts enabling you to develop on
> the modules of the inference stack, and the `oasst-shared` package, without
> rebuilding.

> **Note:** You can spin up any number of workers by adjusting the number of
> replicas of the `inference-worker` service to your liking.

> **Note:** Please wait for the `inference-text-generation-server` service to
> output `{"message":"Connected"}` before starting to chat.


Run the text client:

```bash
cd text-client
pip install -r requirements.txt
python __main__.py
```

## Distributed Testing

We run distributed load tests using the
[`locust`](https://github.com/locustio/locust) Python package.

```bash
pip install locust
cd tests/locust
locust
```

Navigate to http://0.0.0.0:8089/ to view the locust UI.

