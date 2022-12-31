#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../backend"

export DEBUG_SKIP_API_KEY_CHECK=True

python -m print_openapi_schema > oasst-openapi.json

MOCK_SERVER_PORT=8080

docker run --init --rm -d \
  -p $MOCK_SERVER_PORT:4010 \
  -v $(pwd):/tmp \
  -P stoplight/prism:4 \
  mock -h 0.0.0.0 "/tmp/oasst-openapi.json"


popd

