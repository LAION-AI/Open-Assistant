# OpenAssitant Workers

## Running the worker

To run the worker, you need to have docker installed, including the docker
nvidia runtime if you want to use a GPU. We made a convenience-script you can
download and run to start the worker:

```bash
curl -sL https://raw.githubusercontent.com/LAION-AI/Open-Assistant/main/inference/worker/run_worker_container.sh | bash
```

This will download the latest version of the worker and start it.

You can configure the script by setting the following environment variables
(they go before the `bash`)):

- `IMAGE_TYPE` (default: `full`): Set to `llama` for llama models
- `CUDA_VISIBLE_DEVICES` (default: `0,1,2,3,4,5,6,7`): Set to the GPU you want
  to use
- `MODEL_CONFIG_NAME`: Set to the name of the model config you want to use, see
  [here](https://github.com/LAION-AI/Open-Assistant/blob/main/oasst-shared/oasst_shared/model_configs.py),
  for example `OA_SFT_Llama_30Bq`.
- `API_KEY`: Set to the API key you want to use for the worker
- `MAX_PARALLEL_REQUESTS` (default: `1`): Set to the maximum number of parallel
  requests the worker should handle. Set this if you know what you're doing.
- `BACKEND_URL` (default: `wss://inference.prod2.open-assistant.io`): Set to the
  URL of the backend websocket endpoint you want to connect to
- `LOGURU_LEVEL` (default: `INFO`): Set to the log level you want to use.
- `OAHF_HOME` (default: `$HOME/.oasst_cache/huggingface`): Set to the directory
  where you want to store the HF cache. The user for new files will be root, so
  be careful in case you set this to your own `$HOME/.cache/huggingface` (but
  you can save space like that).

## Choosing a model config

Here is how to know whether your GPU supports a model config: Take the number of
parameters of the model in billion and multiply it by 2.5, except if the model
config ends in "q" (quantized to `int8`), in which case multiply it by 1.25.
That number is the minimum Gigabytes of Memory your GPU needs to have. For
example, the `OA_SFT_Llama_30B` model config has 30 billion parameters, so it
needs at least 75 GB of memory, while the `OA_SFT_Llama_30Bq` model only needs
like 40ish GB of memory, due to the quantization.

## Choosing `MAX_PARALLEL_REQUESTS`

If you have a lot of spare GPU memory compared to what your model needs, you can
increase `MAX_PARALLEL_REQUESTS` to increase the throughput of the worker. We
have an OOM test program in the worker to figure out how far you can go, but
it's best to contact us on Discord if you want to do that.
