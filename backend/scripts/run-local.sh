#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../"

export ALLOW_ANY_API_KEY=True

uvicorn app.main:app --reload

popd
