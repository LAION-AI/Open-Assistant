#!/bin/bash

function cleanup {
    echo "Stopping script"
    exit 0
}

# Set up a trap to catch the SIGINT signal (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

image_tag=${IMAGE_TAG:-latest}

# worker image name
image_name="ghcr.io/laion-ai/open-assistant/oasst-inference-worker-full:$image_tag"

# get visible gpu env variable, default to all
gpus=${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}
api_key=${API_KEY:-0000}
backend_url=${BACKEND_URL:-wss://inference.prod.open-assistant.io}
model_id=${MODEL_ID:-OpenAssistant/oasst_sft_llama_13b_mask_1500}

while true; do
    docker pull $image_name
    docker run --rm --privileged --runtime=nvidia --gpus=all \
    -e CUDA_VISIBLE_DEVICES=$gpus \
    -e LOGURU_LEVEL=INFO \
    -e API_KEY=$api_key \
    -e MODEL_ID=$MODEL_ID \
    -e BACKEND_URL=$BACKEND_URL \
    -e HF_TOKEN=$HF_TOKEN \
    $image_name
done
