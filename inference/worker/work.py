import threading

import interface
import requests
import sseclient
import tokenizers
import utils
import websocket
from loguru import logger
from oasst_shared.schemas import inference
from settings import settings

tokenizer_lock = threading.Lock()


def truncate_prompt(tokenizer: tokenizers.Tokenizer, parameters: interface.GenerateStreamParameters, prompt: str):
    with tokenizer_lock:
        encoding: tokenizers.Encoding = tokenizer.encode(prompt)
    ids = encoding.ids
    if len(ids) > settings.max_input_length:
        logger.warning(f"Prompt too long, left-truncating to {settings.max_input_length} tokens")
        ids = ids[-(settings.max_input_length - 1) :]
        with tokenizer_lock:
            prompt = tokenizer.decode(ids)

    input_length = len(ids)
    spare = settings.max_total_tokens - input_length - 1
    if parameters.max_new_tokens > spare:
        logger.warning(f"Max new tokens too high, reducing to {spare}")
        parameters.max_new_tokens = spare
    return prompt


V2_ASST_PREFIX = "<|assistant|>"
V2_PROMPTER_PREFIX = "<|prompter|>"


def make_prompt_and_parameters(
    tokenizer: tokenizers.Tokenizer,
    work_request: inference.WorkRequest,
) -> tuple[str, interface.GenerateStreamParameters]:
    if settings.oa_protocol_version != "v2":
        raise RuntimeError(f"Unsupported oa protocol version: {settings.oa_protocol_version}")

    eos_token = ""
    if hasattr(tokenizer, "eos_token"):
        eos_token = tokenizer.eos_token

    def _prepare_message(message: inference.MessageRead) -> str:
        prefix = V2_ASST_PREFIX if message.is_assistant else V2_PROMPTER_PREFIX
        return prefix + message.content + eos_token

    # construct prompt
    messages = [_prepare_message(message) for message in work_request.thread.messages]

    prompt = "".join(messages) + V2_ASST_PREFIX

    parameters = interface.GenerateStreamParameters.from_work_parameters(work_request.parameters)
    parameters.stop = [
        V2_PROMPTER_PREFIX,
        V2_ASST_PREFIX,
    ]
    if eos_token:
        parameters.stop.append(eos_token)

    return prompt, parameters


def handle_work_request(
    ws: websocket.WebSocket,
    tokenizer: tokenizers.Tokenizer,
    work_request: inference.WorkRequest,
):
    prompt, parameters = make_prompt_and_parameters(tokenizer, work_request)
    logger.debug(f"Prompt: {prompt}")

    stream_response = None
    token_buffer = utils.TokenBuffer(stop_sequences=parameters.stop)
    if settings.model_id == "_lorem":
        stream_events = utils.lorem_events(parameters.seed)
    else:
        prompt = truncate_prompt(tokenizer, parameters, prompt)
        stream_events = get_inference_server_stream_events(parameters, prompt)
    for stream_response in stream_events:
        if stream_response.is_error:
            logger.error(f"Error from inference server: {stream_response.error}")
            utils.send_response(
                ws,
                inference.ErrorResponse(
                    request_id=work_request.id,
                    error=stream_response.error,
                ),
            )
            raise RuntimeError(f"Error from inference server: {stream_response.error}")
        token = stream_response.token
        for send_token in token_buffer.add(token):
            utils.send_response(ws, send_token.to_token_response(request_id=work_request.id))

    if stream_response is None:
        logger.error("No stream response received")
        raise RuntimeError("No stream response received")

    for send_token in token_buffer.finish(reason=stream_response.details.finish_reason):
        utils.send_response(
            ws,
            send_token.to_token_response(request_id=work_request.id),
        )

    utils.send_response(
        ws,
        inference.GeneratedTextResponse(
            request_id=work_request.id,
            text=stream_response.generated_text,
            finish_reason=stream_response.details.finish_reason,
        ),
    )
    logger.info("Work complete. Waiting for more work...")


def get_inference_server_stream_events(parameters: interface.GenerateStreamParameters, prompt: str):
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
