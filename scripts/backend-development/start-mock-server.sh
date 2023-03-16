#!/usr/bin/env bash

function die() {
    popd > /dev/null
    echo "Mock server failed to start"
    exit 1
}

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../backend" > /dev/null

MOCK_SERVER_PORT=8080
OPENAPI_JSON_FILE_NAME=openapi.json

echo "Generating OpenAPI schema..."
python -m main --print-openapi-schema > $OPENAPI_JSON_FILE_NAME || die
echo "Done!"

echo "Formatting & Copying OpenAPI schema to docs directory..."
jq . $OPENAPI_JSON_FILE_NAME > ../docs/docs/api/openapi.json

# If oasst-mock-backend docker container is already running,
# just restart it
if [ "$(docker ps -q -f name=oasst-mock-backend)" ]; then
    echo "oasst-mock-backend container exists, restarting..."
    docker restart oasst-mock-backend
else
    echo "Creating new oasst-mock-backend container..."
    docker run --init --rm -d \
      --name oasst-mock-backend \
      -p $MOCK_SERVER_PORT:4010 \
      -v $(pwd):/tmp \
      -P stoplight/prism:4 \
      mock -h 0.0.0.0 "/tmp/$OPENAPI_JSON_FILE_NAME"
fi

echo "Waiting for server to be live..."
curl --retry-all-errors --retry 10 --silent localhost:$MOCK_SERVER_PORT > /dev/null || die
echo ""

echo "Mock server is running at localhost:$MOCK_SERVER_PORT"
popd
