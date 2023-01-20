# OpenAssistant Inference Server

Workers communicate with the `/work` endpoint. They provide their configuration
and if a task is available, the server returns it. The server also returns the
key of a Redis list where the worker should push the results.

Clients communicate first with the `/complete` endpoint to place a request for
prompt completion. The server returns a unique ID for the request. The client
then polls the `/stream` endpoint with the ID to check if the request has been
assigned to a worker. Once it is assigned, the response will be a SSE event
source.

Notably, `/complete` could be proxied via a frontend, while `/stream` can be
accessed directly by the client, since the unique ID provides enough security.
