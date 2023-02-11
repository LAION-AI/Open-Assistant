#!/bin/bash

text-generation-launcher &

/opt/miniconda/envs/worker/bin/python /worker &

wait -n

exit $?
