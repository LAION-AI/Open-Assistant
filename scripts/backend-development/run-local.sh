#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../backend"

export DEBUG_USE_SEED_DATA=True
export DEBUG_SKIP_TOXICITY_CALCULATION=True
export DEBUG_ALLOW_SELF_LABELING=True
export DEBUG_ALLOW_SELF_RANKING=True
export DEBUG_ALLOW_DUPLICATE_TASKS=True
export DEBUG_SKIP_EMBEDDING_COMPUTATION=True

uvicorn main:app --reload --port 8080 --host 0.0.0.0

popd
