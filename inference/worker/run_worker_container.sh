#!/bin/bash

function cleanup {
    echo "Stopping script"
    exit 0
}

# Set up a trap to catch the SIGINT signal (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

image_name="ghcr.io/laion-ai/open-assistant/oasst-inference-worker-full:latest"

while true; do
    docker pull $image_name
    docker run --rm -it -e retry_on_error=False $image_name
done
