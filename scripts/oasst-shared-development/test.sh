#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# switch to backend directory
pushd "$parent_path/../../oasst-shared"

set -xe

pytest .

popd
