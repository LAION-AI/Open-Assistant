#!/bin/bash
text-generation-launcher &

export INFERENCE_SERVER_URL="http://localhost:80"

/opt/miniconda/envs/worker/bin/python /worker &

wait -n

exit $?
