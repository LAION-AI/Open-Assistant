#!/bin/bash

mkdir -p $HOME/.cache/huggingface
echo -n "$HF_TOKEN" > $HOME/.cache/huggingface/token

uvicorn main:app --host 0.0.0.0 --port "$PORT"
