#!/bin/bash

# read PARALLELISM from env or set to 1 if not set
PARALLELISM=${PARALLELISM:-1}

text-generation-launcher &

# launch PARALLELISM workers
for i in $(seq 1 $PARALLELISM); do
    /opt/miniconda/envs/worker/bin/python /worker &
done

wait -n

exit $?
