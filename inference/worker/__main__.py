import interface
import rel
import requests
import sseclient
import utils
import websocket
from loguru import logger
from oasst_shared.schemas import inference
from settings import settings
from tokenizers import Tokenizer

# touch


def main():
    logger.info(f"Inference protocol version: {inference.INFERENCE_PROTOCOL_VERSION}")

    tokenizer = Tokenizer.from_pretrained(settings.model_id)
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
        logger.info(f"Received {work_request=}")
        parameters = interface.GenerateStreamParameters.from_work_parameters(work_request.parameters)

        def _prepare_message(message: inference.MessageRead) -> str:
            prefix = "Assistant: " if message.is_assistant else "User: "
            return prefix + message.content

        # construct prompt
        messages = [_prepare_message(message) for message in work_request.thread.messages]

        prompt = settings.prefix + "\n".join(messages) + "\nAssistant:"

        encoding = tokenizer.encode(prompt)
        ids = encoding.ids
        if len(ids) > settings.max_input_length:
            logger.warning(f"Prompt too long, left-truncating to {settings.max_input_length} tokens")
            ids = ids[-(settings.max_input_length - 1) :]
            prompt = tokenizer.decode(ids)

        input_length = len(ids)
        spare = settings.max_total_tokens - input_length - 1
        if parameters.max_new_tokens > spare:
            logger.warning(f"Max new tokens too high, reducing to {spare}")
            parameters.max_new_tokens = spare

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
            ws.close()
            return

        client = sseclient.SSEClient(response)
        stream_response = None
        token_buffer = utils.TokenBuffer(stop_sequences=parameters.stop)
        for event in client.events():
            stream_response = interface.GenerateStreamResponse.parse_raw(event.data)
            if stream_response.is_error:
                logger.error(f"Error from inference server: {stream_response.error}")
                ws.send(
                    inference.WorkResponsePacket(
                        error=stream_response.error,
                    ).json()
                )
                ws.close()
                return
            token = stream_response.token
            for send_token in token_buffer.add(token):
                ws.send(
                    inference.WorkResponsePacket(
                        token=send_token.to_token_response(),
                    ).json()
                )

        if stream_response is None:
            logger.error("No stream response received")
            ws.close()
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
        except websocket.WebSocketBadStatusException as e:
            logger.error(f"Bad status: {e.status_code=} {str(e)=}")
            logger.error("Did you provide the correct API key?")
            logger.error("Try upgrading the worker to get the latest protocol version")
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
        header={
            "X-API-Key": settings.api_key,
            "X-Protocol-Version": inference.INFERENCE_PROTOCOL_VERSION,
        },
    )

    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)
    rel.dispatch()


if __name__ == "__main__":
    main()
