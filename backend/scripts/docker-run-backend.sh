#!/bin/bash

# This script launches a ocgpt-backend docker container stand-alone.

docker run -it --rm -p 127.0.0.1:8000:80/tcp --env POSTGRES_SERVER=host.docker.internal:5432 --env ALLOW_ANY_API_KEY=True --add-host host.docker.internal:host-gateway laion-ai/ocgpt-backend
