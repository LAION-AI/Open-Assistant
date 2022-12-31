#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../backend"

export DEBUG_SKIP_API_KEY_CHECK=True

python -m print_openapi_schema > oasst-openapi.json

MOCK_SERVER_PORT=8080

docker run -d -it --rm \
  -p $MOCK_SERVER_PORT:8080 \
  --name wiremock \
  wiremock/wiremock:2.35.0

sleep 1

curl -X POST -d @oasst-openapi.json http://localhost:$MOCK_SERVER_PORT/__admin/mappings/import

popd
