# OpenAssistant Inference Server

Workers communicate with the `/work` endpoint via Websocket. They provide their
configuration and if a task is available, the server returns it. The worker then
performs the task and returns the result in a streaming fashion to the server,
also via websocket.

Clients communicate first with the `/complete` endpoint to place a request for
prompt completion. The server returns a unique ID for the request. The client
then calls the `/stream` endpoint with the ID to get an SSE event source.

Notably, `/complete` could be proxied via a frontend, while `/stream` can be
accessed directly by the client, since the unique ID provides enough security.
