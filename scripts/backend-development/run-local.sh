#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../backend"

export DEBUG_SKIP_API_KEY_CHECK=True
export DEBUG_USE_SEED_DATA=True

uvicorn main:app --reload --port 8080 --host 0.0.0.0

popd
