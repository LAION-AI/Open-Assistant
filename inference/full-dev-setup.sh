#!/bin/bash

# set MODEL_ID to first argument or default to distilgpt2
MODEL_ID=${1:-distilgpt2}

# Creates a tmux window with splits for the individual services

tmux new-session -d -s "inference-dev-setup"
tmux send-keys "docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name postgres postgres" C-m
tmux split-window -h
tmux send-keys "docker run --rm -it -p 6379:6379 --name redis redis" C-m
tmux split-window -h
tmux send-keys "docker run --rm -it -p 8001:80 -e MODEL_ID=distilgpt2 \
    -v $HOME/.cache/huggingface:/root/.cache/huggingface \
    --name text-generation-inference ghcr.io/yk/text-generation-inference" C-m
tmux split-window -h
tmux send-keys "cd server" C-m
tmux send-keys "DEBUG_API_KEYS='[\"0000\", \"0001\"]' ALLOW_DEBUG_AUTH=True uvicorn main:app" C-m
tmux split-window -h
tmux send-keys "cd text-client" C-m
tmux send-keys "sleep 5" C-m
tmux send-keys "python __main__.py --model-id=$MODEL_ID" C-m
tmux split-window -h
tmux send-keys "cd worker" C-m
tmux send-keys "API_KEY=0000 MODEL_ID=$MODEL_ID python __main__.py" C-m
tmux split-window -v
tmux send-keys "cd worker" C-m
tmux send-keys "API_KEY=0001 MODEL_ID=$MODEL_ID python __main__.py" C-m
tmux select-layout even-horizontal
tmux attach-session -t "inference-dev-setup"
