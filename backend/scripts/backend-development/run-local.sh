#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../app"

export ALLOW_ANY_API_KEY=True

uvicorn main:app --reload --port 8080 --host 0.0.0.0

popd
