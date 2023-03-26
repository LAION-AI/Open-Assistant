#!/bin/bash

mkdir -p $HOME/.cache/huggingface
echo -n "$HF_TOKEN" > $HOME/.cache/huggingface/token

export MODEL_CONFIG_NAME=${MODEL_CONFIG_NAME:-"OA_SFT_Pythia_12B"}

num_shards=${NUM_SHARDS:-1}

export MODEL_ID=$(/opt/miniconda/envs/worker/bin/python /worker/get_model_config_prop.py model_id)
export QUANTIZE=$(/opt/miniconda/envs/worker/bin/python /worker/get_model_config_prop.py quantized)

quantize=${QUANTIZE:-"false"}
quantize_args=""
if [ "$quantize" = "true" ]; then
    quantize_args="--quantize"
fi

export HF_HUB_ENABLE_HF_TRANSFER=
export HF_HOME=$HOME/.cache/huggingface
export HUGGING_FACE_HUB_TOKEN=$HF_TOKEN
/opt/miniconda/envs/text-generation/bin/python /worker/download_model.py

text-generation-launcher --model-id $MODEL_ID --num-shard $num_shards $quantize_args &

export INFERENCE_SERVER_URL="http://localhost:80"

/opt/miniconda/envs/worker/bin/python /worker &

wait -n

exit $?
