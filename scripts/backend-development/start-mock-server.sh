#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../backend"

MOCK_SERVER_PORT=8080
OPENAPI_JSON_FILE_NAME=openapi.json

echo "Generating OpenAPI schema..."
python -m print_openapi_schema > $OPENAPI_JSON_FILE_NAME
echo "Done!"

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
curl --retry-all-errors --retry 5 localhost:$MOCK_SERVER_PORT
echo ""

# if return code is successful, print successful response
if [ $? -eq 0 ]; then
    echo "Mock server is running at localhost:$MOCK_SERVER_PORT"
else
    echo "Mock server failed to start"
fi


popd

