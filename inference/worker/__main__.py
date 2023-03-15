import signal
import sys
import time
from contextlib import closing

import interface
import lorem
import pydantic
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
            raise
        except Exception:
            logger.exception("Error in websocket")
            logger.info("Retrying in 5 seconds...")
            if not settings.retry_on_error:
                sys.exit(1)
            time.sleep(5)


def send_response(
    ws: websocket.WebSocket,
    repsonse: inference.WorkerResponse | inference.WorkerConfig,
):
    ws.send(repsonse.json())


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
        send_response(ws, worker_config)
        logger.info("Config sent, waiting for work...")

        while True:
            message = ws.recv()
            # TODO: what if this comes in, but one is already in progress?
            # also need to think of enabling batching

            worker_request = pydantic.parse_raw_as(inference.WorkerRequest, message)
            logger.debug(f"Received {worker_request=}")
            match worker_request.request_type:
                case "work":
                    do_work(ws, tokenizer, worker_request)
                case "ping":
                    logger.debug("Received ping, sending pong")
                    send_response(ws, inference.PongResponse())
                case "terminate":
                    logger.info("Received terminate, terminating worker")
                    sys.exit(0)
                case "error":
                    logger.error(f"Received error: {worker_request.error}")
                    raise RuntimeError(f"Received error: {worker_request.error}")


V2_ASST_PREFIX = "<|assistant|>"
V2_PROMPTER_PREFIX = "<|prompter|>"
V2_ENDOFTEXT = "<|endoftext|>"


def make_prompt_and_parameters(
    work_request: inference.WorkRequest,
) -> tuple[str, interface.GenerateStreamParameters]:
    if settings.oa_protocol_version != "v2":
        raise RuntimeError(f"Unsupported oa protocol version: {settings.oa_protocol_version}")

    def _prepare_message(message: inference.MessageRead) -> str:
        prefix = V2_ASST_PREFIX if message.is_assistant else V2_PROMPTER_PREFIX
        return prefix + message.content + V2_ENDOFTEXT

    # construct prompt
    messages = [_prepare_message(message) for message in work_request.thread.messages]

    prompt = "".join(messages) + V2_ASST_PREFIX

    parameters = interface.GenerateStreamParameters.from_work_parameters(work_request.parameters)

    return prompt, parameters


def do_work(
    ws: websocket.WebSocket,
    tokenizer: tokenizers.Tokenizer,
    work_request: inference.WorkRequest,
):
    prompt, parameters = make_prompt_and_parameters(work_request)
    logger.debug(f"Prompt: {prompt}")

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
            send_response(
                ws,
                inference.ErrorResponse(
                    error=stream_response.error,
                ),
            )
            raise RuntimeError(f"Error from inference server: {stream_response.error}")
        token = stream_response.token
        for send_token in token_buffer.add(token):
            send_response(ws, send_token.to_token_response())

    if stream_response is None:
        logger.error("No stream response received")
        raise RuntimeError("No stream response received")

    for send_token in token_buffer.finish(reason=stream_response.details.finish_reason):
        send_response(
            ws,
            send_token.to_token_response(),
        )

    send_response(
        ws,
        inference.GeneratedTextResponse(
            text=stream_response.generated_text,
            finish_reason=stream_response.details.finish_reason,
        ),
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
