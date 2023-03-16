#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
docker compose -f "$parent_path/../../docker-compose.yaml" --profile backend-dev up --build --attach-dependencies
