#!/bin/bash

mkdir -p $HOME/.cache/huggingface
echo -n "$HF_TOKEN" > $HOME/.cache/huggingface/token

python3 -m uvicorn --port 8883 basic_hf_server:app &

export INFERENCE_SERVER_URL="http://localhost:8883"
export MAX_PARALLEL_REQUESTS=${MAX_PARALLEL_REQUESTS:-1}

python3 __main__.py &

wait -n

exit $?
