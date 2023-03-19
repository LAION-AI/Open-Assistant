#!/bin/bash

mkdir -p $HOME/.huggingface
echo -n "$HF_TOKEN" > $HOME/.huggingface/token

uvicorn main:app --host 0.0.0.0 --port "$PORT"
