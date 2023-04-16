#!/bin/bash

export HF_HOME=${HF_HOME:-"$HOME/.cache/huggingface"}
load_sleep=${LOAD_SLEEP:-0}

mkdir -p $HF_HOME
echo -n "$HF_TOKEN" > $HF_HOME/token

export HUGGING_FACE_HUB_TOKEN=$HF_TOKEN

export MODEL_CONFIG_NAME=${MODEL_CONFIG_NAME:-"OA_SFT_Pythia_12B"}
export MODEL_ID=$(python get_model_config_prop.py model_id)
export QUANTIZE=$(python get_model_config_prop.py quantized)

echo "Downloading model $MODEL_ID"
CUDA_VISIBLE_DEVICES="" python download_model_hf.py

export MAX_PARALLEL_REQUESTS=${MAX_PARALLEL_REQUESTS:-1}

echo "starting worker"
python3 __main__.py
