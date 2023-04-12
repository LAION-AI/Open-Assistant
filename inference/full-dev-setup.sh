#!/bin/bash

# set MODEL_CONFIG_NAME to first argument or default to distilgpt2
export MODEL_CONFIG_NAME=${1:-distilgpt2}
MODEL_ID=$(python3 worker/get_model_config_prop.py model_id)
LOGLEVEL=${LOGLEVEL:-DEBUG}
echo "MODEL_ID: $MODEL_ID"
is_llama=$(python3 worker/get_model_config_prop.py is_llama)
# if model is a llama, use the llama tag
if [ "$is_llama" = "true" ]; then
    INFERENCE_TAG=llama
else
    INFERENCE_TAG=latest
fi

# Creates a tmux window with splits for the individual services

tmux new-session -d -s "inference-dev-setup"
tmux send-keys "docker run --rm -it -p 5732:5432 -e POSTGRES_PASSWORD=postgres --name postgres postgres" C-m
tmux split-window -h
tmux send-keys "docker run --rm -it -p 6779:6379 --name redis redis" C-m

# only if model is not _lorem
if [ "$MODEL_CONFIG_NAME" != "_lorem" ]; then
tmux split-window -h
tmux send-keys "docker run --rm -it -p 8001:80 -e MODEL_ID=$MODEL_ID \
    -v $HOME/.cache/huggingface:/root/.cache/huggingface \
    --name text-generation-inference ghcr.io/yk/text-generation-inference:$INFERENCE_TAG" C-m
fi

tmux split-window -h
tmux send-keys "cd server" C-m
tmux send-keys "LOGURU_LEVEL=$LOGLEVEL POSTGRES_PORT=5732 REDIS_PORT=6779 DEBUG_API_KEYS='0000,0001' ALLOW_DEBUG_AUTH=True uvicorn main:app" C-m
tmux split-window -h
tmux send-keys "cd text-client" C-m
tmux send-keys "sleep 5" C-m
tmux send-keys "LOGURU_LEVEL=$LOGLEVEL python __main__.py --model-config-name=$MODEL_CONFIG_NAME" C-m
tmux split-window -h
tmux send-keys "cd worker" C-m
tmux send-keys "LOGURU_LEVEL=$LOGLEVEL API_KEY=0000 MODEL_CONFIG_NAME=$MODEL_CONFIG_NAME python __main__.py" C-m
tmux split-window -v
tmux send-keys "cd worker" C-m
tmux send-keys "LOGURU_LEVEL=$LOGLEVEL API_KEY=0001 MODEL_CONFIG_NAME=$MODEL_CONFIG_NAME python __main__.py" C-m
tmux select-layout even-horizontal
tmux attach-session -t "inference-dev-setup"
