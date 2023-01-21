# OpenAssistant Inference Server

Workers communicate with the `/work` endpoint via Websocket. They provide their
configuration and if a task is available, the server returns it. The worker then
performs the task and returns the result in a streaming fashion to the server,
also via websocket.

Clients first call `/chat` to make a new chat, then add to that via
`/chat/<id>/message`. The response is a SSE event source, which will send tokens
as they are available.
