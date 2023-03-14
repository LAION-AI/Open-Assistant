import signal
import sys
import time
from contextlib import closing

import interface
import lorem
import requests
import sseclient
import tokenizers
import utils
import websocket
from loguru import logger
from oasst_shared.schemas import inference
from settings import settings


def terminate_worker(signum, frame):
    logger.info(f"Signal {signum}. Terminating worker...")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, terminate_worker)
    logger.info(f"Inference protocol version: {inference.INFERENCE_PROTOCOL_VERSION}")

    if settings.model_id != "_lorem":
        tokenizer = tokenizers.Tokenizer.from_pretrained(settings.model_id)
    else:
        tokenizer = None

    while True:
        try:
            if settings.model_id != "_lorem":
                utils.wait_for_inference_server(settings.inference_server_url)
            connect_and_do_work(tokenizer)

        except websocket.WebSocketBadStatusException as e:
            logger.error(f"Bad status: {e.status_code=} {str(e)=}")
            logger.error("Did you provide the correct API key?")
            logger.error("Try upgrading the worker to get the latest protocol version")
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            break
        except Exception:
            logger.exception("Error in websocket")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)


def connect_and_do_work(tokenizer: tokenizers.Tokenizer):
    with closing(
        websocket.create_connection(
            f"{settings.backend_url}/workers/work",
            header={
                "X-API-Key": settings.api_key,
                "X-Protocol-Version": inference.INFERENCE_PROTOCOL_VERSION,
            },
        )
    ) as ws:
        logger.info("Connected to backend, sending config...")
        worker_config = inference.WorkerConfig(model_name=settings.model_id)
        ws.send(worker_config.json())
        logger.info("Config sent, waiting for work...")

        while True:
            message = ws.recv()
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

            prompt = settings.prefix + "\n".join(messages) + "\nAssistant: "

            stream_response = None
            token_buffer = utils.TokenBuffer(stop_sequences=parameters.stop)
            if settings.model_id == "_lorem":

                def _lorem_events(parameters=parameters):
                    sentence = lorem.sentence()
                    print(sentence)
                    tokens = sentence.split()
                    for token in tokens[:-1]:
                        yield interface.GenerateStreamResponse(
                            token=interface.Token(
                                text=token + " ",
                                logprob=0.1,
                                id=0,
                            ),
                        )
                    yield interface.GenerateStreamResponse(
                        token=interface.Token(
                            text=tokens[-1],
                            logprob=0.1,
                            id=0,
                        ),
                        generated_text=sentence,
                        details=interface.StreamDetails(
                            finish_reason="length",
                            generated_tokens=len(tokens),
                            seed=parameters.seed,
                        ),
                    )

                stream_events = _lorem_events()
            else:
                stream_events = get_stream_events(tokenizer, parameters, prompt)
            for stream_response in stream_events:
                if stream_response.is_error:
                    logger.error(f"Error from inference server: {stream_response.error}")
                    ws.send(
                        inference.ErrorResponse(
                            error=stream_response.error,
                        ).json()
                    )
                    raise RuntimeError(f"Error from inference server: {stream_response.error}")
                token = stream_response.token
                for send_token in token_buffer.add(token):
                    ws.send(
                        send_token.to_token_response().json(),
                    )

            if stream_response is None:
                logger.error("No stream response received")
                raise RuntimeError("No stream response received")

            for send_token in token_buffer.finish(reason=stream_response.details.finish_reason):
                ws.send(
                    send_token.to_token_response().json(),
                )

            ws.send(
                inference.GeneratedTextResponse(
                    text=stream_response.generated_text,
                    finish_reason=stream_response.details.finish_reason,
                ).json()
            )
            logger.info("Work complete. Waiting for more work...")


def get_stream_events(tokenizer, parameters, prompt):
    encoding: tokenizers.Encoding = tokenizer.encode(prompt)
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
        raise

    client = sseclient.SSEClient(response)
    for event in client.events():
        stream_response = interface.GenerateStreamResponse.parse_raw(event.data)
        yield stream_response


if __name__ == "__main__":
    main()
