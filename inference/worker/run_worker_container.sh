#!/bin/bash

function cleanup {
    echo "Stopping script"
    exit 0
}

# Set up a trap to catch the SIGINT signal (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

image_tag=${IMAGE_TAG:-latest}
image_type=${IMAGE_TYPE:-full}

# worker image name
image_name="ghcr.io/laion-ai/open-assistant/oasst-inference-worker-$image_type:$image_tag"

# get visible gpu env variable, default to all
gpus=${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}
api_key=${API_KEY:-0000}
backend_url=${BACKEND_URL:-wss://inference.prod.open-assistant.io}
model_id=${MODEL_ID:-OpenAssistant/oasst_sft_llama_13b_mask_1500}
max_parallel_requests=${MAX_PARALLEL_REQUESTS:-8}
loguru_level=${LOGURU_LEVEL:-INFO}
quantize=${QUANTIZE:-false}

OAHF_HOME=$HOME/.oasst_cache/huggingface
mkdir -p $OAHF_HOME

while true; do
    docker pull $image_name
    docker run -it --rm --privileged --runtime=nvidia --gpus=all \
    -e CUDA_VISIBLE_DEVICES=$gpus \
    -e LOGURU_LEVEL=$loguru_level \
    -e API_KEY=$api_key \
    -e MODEL_ID=$model_id \
    -e BACKEND_URL=$backend_url \
    -e HF_TOKEN=$HF_TOKEN \
    -e MAX_PARALLEL_REQUESTS=$max_parallel_requests \
    -e QUANTIZE=$quantize \
    -e HF_HUB_ENABLE_HF_TRANSFER= \
    -v $OAHF_HOME:/data \
    $image_name
done
