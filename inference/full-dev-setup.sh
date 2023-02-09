#!/bin/bash

# Creates a tmux window with splits for the individual services

tmux new-session -d -s "inference-dev-setup"
tmux send-keys "docker run --rm -it -p 6379:6379 redis" C-m
tmux split-window -h
tmux send-keys "docker run --rm -it -p 8001:80 -e MODEL_ID=distilgpt2 ghcr.io/huggingface/text-generation-inference" C-m
tmux split-window -h
tmux send-keys "cd server" C-m
tmux send-keys "uvicorn main:app --reload" C-m
tmux split-window -h
tmux send-keys "cd worker" C-m
tmux send-keys "python __main__.py" C-m
tmux split-window -h
tmux send-keys "cd text-client" C-m
tmux send-keys "sleep 5" C-m
tmux send-keys "python __main__.py" C-m
tmux select-layout even-horizontal
tmux attach-session -t "inference-dev-setup"
