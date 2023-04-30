#!/bin/bash

export HF_HOME=${HF_HOME:-"$HOME/.cache/huggingface"}
load_sleep=${LOAD_SLEEP:-0}

mkdir -p $HF_HOME
echo -n "$HF_TOKEN" > $HF_HOME/token

export HUGGING_FACE_HUB_TOKEN=$HF_TOKEN

export MODEL_CONFIG_NAME=${MODEL_CONFIG_NAME:-"OA_SFT_Pythia_12B"}
export MODEL_ID=$(python get_model_config_prop.py model_id)
export QUANTIZE=$(python get_model_config_prop.py quantized)

echo "Downloading model $MODEL_ID"
CUDA_VISIBLE_DEVICES="" python download_model_hf.py

export MAX_PARALLEL_REQUESTS=${MAX_PARALLEL_REQUESTS:-1}

# if cuda devices is empty
if [ -z "$CUDA_VISIBLE_DEVICES" ]; then
    worker_port=8300

    echo "Starting worker server on port $worker_port"
    python3 -m uvicorn --host 0.0.0.0 --port $worker_port basic_hf_server:app &
    export INFERENCE_SERVER_URL="http://localhost:$worker_port"

    echo "Starting worker"
    python3 __main__.py &

else
    # split cuda devices and loop over them
    echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
    IFS=',' read -ra devices <<< "$CUDA_VISIBLE_DEVICES"
    for i in "${!devices[@]}"; do
        device="${devices[$i]}"
        worker_port=$((8300 + $i))

        echo "Starting worker server $i on port $worker_port on device $device"
        CUDA_VISIBLE_DEVICES=$device python3 -m uvicorn --host 0.0.0.0 --port $worker_port basic_hf_server:app &

        echo "Starting worker $i"
        CUDA_VISIBLE_DEVICES="" INFERENCE_SERVER_URL="http://localhost:$worker_port" python3 __main__.py &

        sleep $load_sleep
    done
fi

# trap to kill all running processes on ctrl-c
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT


wait -n

exit $?
