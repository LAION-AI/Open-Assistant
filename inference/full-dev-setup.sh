#!/bin/bash

# set MODEL_CONFIG_NAME to first argument or default to distilgpt2
MODEL_CONFIG_NAME=${1:-distilgpt2}
MODEL_ID=${2:-$MODEL_CONFIG_NAME}
LOGLEVEL=${LOGLEVEL:-DEBUG}

# Creates a tmux window with splits for the individual services

tmux new-session -d -s "inference-dev-setup"
tmux send-keys "docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name postgres postgres" C-m
tmux split-window -h
tmux send-keys "docker run --rm -it -p 6379:6379 --name redis redis" C-m

# only if model is not _lorem
if [ "$MODEL_CONFIG_NAME" != "_lorem" ]; then
tmux split-window -h
tmux send-keys "docker run --rm -it -p 8001:80 -e MODEL_ID=$MODEL_ID \
    -v $HOME/.cache/huggingface:/root/.cache/huggingface \
    --name text-generation-inference ghcr.io/yk/text-generation-inference:llama" C-m
fi

tmux split-window -h
tmux send-keys "cd server" C-m
tmux send-keys "LOGURU_LEVEL=$LOGLEVEL DEBUG_API_KEYS='0000,0001' ALLOW_DEBUG_AUTH=True uvicorn main:app" C-m
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
