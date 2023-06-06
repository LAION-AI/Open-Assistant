#!/bin/bash

mkdir -p $HOME/.cache/huggingface
echo -n "$HF_TOKEN" > $HOME/.cache/huggingface/token

export MODEL_CONFIG_NAME=${MODEL_CONFIG_NAME:-"OA_SFT_Pythia_12B"}

num_shards=${NUM_SHARDS:-1}
load_sleep=${LOAD_SLEEP:-0}

export MODEL_ID=$(/opt/miniconda/envs/worker/bin/python /worker/get_model_config_prop.py model_id)
export QUANTIZE=$(/opt/miniconda/envs/worker/bin/python /worker/get_model_config_prop.py quantized)

quantize=${QUANTIZE:-"false"}
quantize_args=""
if [ "$quantize" = "true" ]; then
    quantize_args="--quantize"
fi

export HF_HUB_ENABLE_HF_TRANSFER=
export HF_HOME=$HOME/.cache/huggingface
export HUGGING_FACE_HUB_TOKEN=$HF_TOKEN

echo "Downloading model $MODEL_ID"
CUDA_VISIBLE_DEVICES="" /opt/miniconda/envs/text-generation/bin/python /worker/download_model.py

# if cuda devices is empty
if [ -z "$CUDA_VISIBLE_DEVICES" ]; then
    worker_port=8300
    echo "Starting worker server on port $worker_port"
    text-generation-launcher --model-id $MODEL_ID --num-shard $num_shards $quantize_args --port $worker_port &
    export INFERENCE_SERVER_URL="http://localhost:$worker_port"
    echo "Starting worker"
    /opt/miniconda/envs/worker/bin/python /worker &

else
    # split cuda devices and loop over them
    echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
    IFS=',' read -ra devices <<< "$CUDA_VISIBLE_DEVICES"
    for i in "${!devices[@]}"; do
        device="${devices[$i]}"
        worker_port=$((8300 + $i))
        master_port=$((29500 + $i))
        shard_uds_path="/tmp/text-generation-server-$i"
        echo "Starting worker server $i on port $worker_port on device $device"
        CUDA_VISIBLE_DEVICES=$device text-generation-launcher --model-id $MODEL_ID --num-shard $num_shards $quantize_args --port $worker_port --master-port $master_port --shard-uds-path $shard_uds_path &
        echo "Starting worker $i"
        CUDA_VISIBLE_DEVICES="" INFERENCE_SERVER_URL="http://localhost:$worker_port" /opt/miniconda/envs/worker/bin/python /worker &
        sleep $load_sleep
    done
fi

wait -n

exit $?
