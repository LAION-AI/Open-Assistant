#!/bin/bash

function cleanup {
    echo "Stopping script"
    exit 0
}

# Set up a trap to catch the SIGINT signal (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# worker image name
image_name="ghcr.io/laion-ai/open-assistant/oasst-inference-worker-full:latest"

# get visible gpu env variable, default to all
gpus=${CUDA_VISIBLE_DEVICES:-all}

while true; do
    docker pull $image_name
    docker run --rm --runtime=nvidia --gpus=$gpus -e RETRY_ON_ERROR=False $image_name
done
