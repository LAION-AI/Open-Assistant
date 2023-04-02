#!/bin/bash

mkdir -p $HOME/.cache/huggingface
echo -n "$HF_TOKEN" > $HOME/.cache/huggingface/token

HF_SERVER_PORT=${HF_SERVER_PORT:-8883}

python3 -m uvicorn --port $HF_SERVER_PORT basic_hf_server:app &

export INFERENCE_SERVER_URL="http://localhost:$HF_SERVER_PORT"
export MAX_PARALLEL_REQUESTS=${MAX_PARALLEL_REQUESTS:-1}

python3 __main__.py &

wait -n

exit $?
