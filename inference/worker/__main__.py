import interface
import rel
import requests
import sseclient
import utils
import websocket
from loguru import logger
from oasst_shared.schemas import inference, protocol
from settings import settings

# touch


def main():
    utils.wait_for_inference_server(settings.inference_server_url)

    def on_open(ws: websocket.WebSocket):
        logger.info("Connected to backend, sending config...")
        worker_config = inference.WorkerConfig(model_name=settings.model_id)
        ws.send(worker_config.json())
        logger.info("Config sent, waiting for work...")

    def on_message(ws: websocket.WebSocket, message: str):
        # TODO: what if this comes in, but one is already in progress?
        # also need to think of enabling batching
        work_request = inference.WorkRequest.parse_raw(message)

        def _prepare_message(message: protocol.ConversationMessage) -> str:
            prefix = "Assistant: " if message.is_assistant else "User: "
            return prefix + message.text

        # construct prompt
        messages = [_prepare_message(message) for message in work_request.conversation.messages]

        prefix = (
            "The following is a conversation between a user and an assistant. "
            "The assistant is helpful, creative, clever, and very friendly.\n"
            "Assistant: Hello! How can I help you today?\n"
        )

        prompt = prefix + "\n".join(messages) + "\nAssistant:"

        parameters = interface.GenerateStreamParameters.from_work_request(work_request)
        response = requests.post(
            f"{settings.inference_server_url}/generate_stream",
            json={
                "inputs": prompt,
                "parameters": parameters.dict(),
            },
            stream=True,
            headers={"Accept": "text/event-stream"},
        )
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.exception("Failed to get response from inference server")
            logger.error(f"Response: {response.text}")
            return

        client = sseclient.SSEClient(response)
        stream_response = None
        token_buffer = utils.TokenBuffer(stop_sequences=parameters.stop)
        for event in client.events():
            logger.debug(f"Received event: {event}")
            stream_response = interface.GenerateStreamResponse.parse_raw(event.data)
            token = stream_response.token
            for send_token in token_buffer.add(token):
                ws.send(
                    inference.WorkResponsePacket(
                        token=send_token.to_token_response(),
                    ).json()
                )
        if stream_response is None:
            logger.error("No stream response received")
            return

        for send_token in token_buffer.finish(reason=stream_response.details.finish_reason):
            ws.send(
                inference.WorkResponsePacket(
                    token=send_token.to_token_response(),
                ).json()
            )

        ws.send(
            inference.WorkResponsePacket(
                is_end=True,
                generated_text=inference.GeneratedTextResponse(
                    text=stream_response.generated_text,
                    finish_reason=stream_response.details.finish_reason,
                ),
            ).json()
        )
        logger.info("Work complete. Waiting for more work...")

    def on_error(ws: websocket.WebSocket, error: Exception):
        try:
            raise error
        except Exception:
            logger.exception("Error in websocket")

    def on_close(ws: websocket.WebSocket, close_status_code: int, close_msg: str):
        logger.warning(f"Connection closed: {close_status_code=} {close_msg=}")

    ws = websocket.WebSocketApp(
        f"{settings.backend_url}/work",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
        header={"X-API-Key": settings.api_key},
    )

    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)
    rel.dispatch()


if __name__ == "__main__":
    main()
