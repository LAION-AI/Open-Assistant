#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
pushd $parent_path

docker build ../../backend -f ../backend.dockerfile -t laion-ai/ocgpt-backend

popd
