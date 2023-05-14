#!/bin/bash

export HF_HOME=${HF_HOME:-"$HOME/.cache/huggingface"}
load_sleep=${LOAD_SLEEP:-0}

mkdir -p $HF_HOME
echo -n "$HF_TOKEN" > $HF_HOME/token

export HUGGING_FACE_HUB_TOKEN=$HF_TOKEN

export MODEL_CONFIG_NAME=${MODEL_CONFIG_NAME:-"OA_SFT_Pythia_12B"}
export MODEL_ID=$(/opt/venv/bin/python3 get_model_config_prop.py model_id)
export QUANTIZE=$(/opt/venv/bin/python3 get_model_config_prop.py quantized)

# echo "Downloading model $MODEL_ID"
#CUDA_VISIBLE_DEVICES="" /opt/venv/bin/python3 download_model_hf.py

export MAX_PARALLEL_REQUESTS=${MAX_PARALLEL_REQUESTS:-1}

worker_port=8300

echo "Starting worker server on port $worker_port"
/opt/venv/bin/python3 -m uvicorn --host 0.0.0.0 --port $worker_port basic_hf_server:app &
export INFERENCE_SERVER_URL="http://localhost:$worker_port"

echo "Starting worker"

/opt/venv/bin/python /worker &

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

wait -n

exit $?
