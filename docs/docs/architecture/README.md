# Architecture

## Inference

The Inference architecture is comprised of several core components: a text, or
frontend client, a FastAPI webserver, a database with several tables, Reddis
used for queueing, and distributed gpu workers.

A more detailed overview can be viewed [here](inference.md).
