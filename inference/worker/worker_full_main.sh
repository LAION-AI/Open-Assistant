#!/bin/bash

mkdir -p $HOME/.cache/huggingface
echo -n "$HF_TOKEN" > $HOME/.cache/huggingface/token

num_shards=${NUM_SHARDS:-1}
model_id=${MODEL_ID:-"OpenAssistant/oasst-sft-1-pythia-12b"}

export HF_HOME=$HOME/.cache/huggingface
export HUGGING_FACE_HUB_TOKEN=$HF_TOKEN
/opt/miniconda/envs/text-generation/bin/python /worker/download_model.py

text-generation-launcher --model-id $model_id --num-shard $num_shards &

export INFERENCE_SERVER_URL="http://localhost:80"

/opt/miniconda/envs/worker/bin/python /worker &

wait -n

exit $?
