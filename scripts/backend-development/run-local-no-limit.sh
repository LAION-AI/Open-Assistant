#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../backend"

if [[ $1 == hf ]]; then
  echo "Enabling Huggingface service calls..."
  export DEBUG_SKIP_TOXICITY_CALCULATION=False
  export DEBUG_SKIP_EMBEDDING_COMPUTATION=False
else
  export DEBUG_SKIP_TOXICITY_CALCULATION=True
  export DEBUG_SKIP_EMBEDDING_COMPUTATION=True
fi

export DEBUG_USE_SEED_DATA=True
export DEBUG_ALLOW_SELF_LABELING=True
export DEBUG_ALLOW_SELF_RANKING=True
export DEBUG_ALLOW_DUPLICATE_TASKS=True
export RATE_LIMIT=0
export DEBUG_USE_SEED_DATA_PATH=$parent_path/../../backend/test_data/generic/test_generic_data.json

uvicorn main:app --reload --port 8080 --host 0.0.0.0

popd
