import threading
from concurrent import futures

import interface
import requests
import sseclient
import transformers
import utils
import websocket
from loguru import logger
from oasst_shared.schemas import inference
from settings import settings

tokenizer_lock = threading.Lock()


def truncate_prompt(
    tokenizer: transformers.PreTrainedTokenizer,
    worker_config: inference.WorkerConfig,
    parameters: interface.GenerateStreamParameters,
    prompt: str,
):
    with tokenizer_lock:
        ids = tokenizer.encode(prompt)

    max_input_length = worker_config.model_config.max_input_length
    max_total_tokens = worker_config.model_config.max_total_length
    if len(ids) > max_input_length:
        logger.warning(f"Prompt too long, left-truncating to {max_input_length} tokens")
        ids = ids[-(max_input_length - 1) :]
        with tokenizer_lock:
            prompt = tokenizer.decode(ids)

    input_length = len(ids)
    spare = max_total_tokens - input_length - 1
    if not parameters.max_new_tokens:
        parameters.max_new_tokens = spare
    elif parameters.max_new_tokens > spare:
        logger.warning(f"Max new tokens too high, reducing to {spare}")
        parameters.max_new_tokens = spare
    return prompt


V2_ASST_PREFIX = "<|assistant|>"
V2_PROMPTER_PREFIX = "<|prompter|>"


def make_prompt_and_parameters(
    tokenizer: transformers.PreTrainedTokenizer,
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
    if settings.use_stop_sequences:
        parameters.stop = [
            V2_PROMPTER_PREFIX,
            V2_ASST_PREFIX,
        ]
        if eos_token:
            parameters.stop.append(eos_token)
    else:
        parameters.stop = []

    return prompt, parameters


def handle_work_request(
    ws: websocket.WebSocket,
    tokenizer: transformers.PreTrainedTokenizer,
    work_request: inference.WorkRequest,
    worker_config: inference.WorkerConfig,
):
    prompt, parameters = make_prompt_and_parameters(tokenizer=tokenizer, work_request=work_request)
    logger.debug(f"Prompt: {prompt}")

    model_config = worker_config.model_config

    stream_response = None
    token_buffer = utils.TokenBuffer(stop_sequences=parameters.stop)
    stream_request = interface.GenerateStreamRequest(
        inputs=prompt,
        parameters=parameters,
    )
    if model_config.is_lorem:
        stream_events = utils.lorem_events(parameters.seed)
    # elif model_config.is_llama:
    #     prompt = truncate_prompt(tokenizer, worker_config, parameters, prompt)
    #     stream_events = get_hf_stream_events(stream_request)
    else:
        prompt = truncate_prompt(tokenizer, worker_config, parameters, prompt)
        stream_events = get_inference_server_stream_events(stream_request)

    generated_ids = []
    decoded_text = ""
    for stream_response in stream_events:
        if stream_response.is_error:
            logger.error(f"Error from inference server: {stream_response.error}")
            utils.send_response(
                ws,
                inference.ErrorResponse(
                    request_id=work_request.id,
                    error=stream_response.error,
                    metrics=inference.WorkerMetricsInfo(),
                ),
            )
            raise RuntimeError(f"Error from inference server: {stream_response.error}")
        token = stream_response.token

        if model_config.is_llama:
            generated_ids.append(token.id)
            with tokenizer_lock:
                text = tokenizer.decode(generated_ids)
            new_text = text[len(decoded_text) :]
            if not decoded_text:
                new_text = new_text.lstrip()
            token.text = new_text
            decoded_text = text

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

    if model_config.is_llama:
        stream_response.generated_text = stream_response.generated_text.strip()
    logger.info(f"Done. {stream_response=}")
    utils.send_response(
        ws,
        inference.GeneratedTextResponse(
            request_id=work_request.id,
            text=stream_response.generated_text,
            finish_reason=stream_response.details.finish_reason,
            metrics=inference.WorkerMetricsInfo(),
        ),
    )
    logger.debug("Work complete. Waiting for more work...")


def get_hf_stream_events(request: interface.GenerateStreamRequest):
    response = requests.post(
        f"{settings.inference_server_url}/generate",
        json=request.dict(),
    )
    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.exception("Failed to get response from inference server")
        logger.error(f"Response: {response.text}")
        raise
    data = response.json()
    output = data["text"]
    yield from utils.text_to_events(output, pause=settings.hf_pause)


def get_inference_server_stream_events(request: interface.GenerateStreamRequest):
    response = requests.post(
        f"{settings.inference_server_url}/generate_stream",
        json=request.dict(),
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


def perform_oom_test(tokenizer: transformers.PreTrainedTokenizer):
    logger.warning("Performing OOM test")
    prompt = ("This is a test prompt. " * 10000).strip()
    parameters = interface.GenerateStreamParameters(
        max_new_tokens=4,
        temperature=1.5,
        top_p=0.95,
        repetition_penalty=1.0,
        do_sample=True,
        stop=[],
    )

    class OOMError(Exception):
        pass

    if settings.oom_test_max_length is None:
        try:
            for length in range(256, 2**15, 256):
                prompt_ids = tokenizer.encode(prompt, max_length=length - 4, truncation=True)
                short_prompt = tokenizer.decode(prompt_ids)
                stream_request = interface.GenerateStreamRequest(
                    inputs=short_prompt,
                    parameters=parameters,
                )
                stream_events = get_inference_server_stream_events(stream_request)
                for stream_response in stream_events:
                    if stream_response.is_error:
                        logger.error(f"Error from inference server: {stream_response.error}")
                        raise OOMError()
        except OOMError:
            length = length - 256
        logger.warning(f"Max length: {length}")
    else:
        length = settings.oom_test_max_length

    with futures.ThreadPoolExecutor() as executor:
        try:
            for batch_size in range(1, 32, 1):
                prompt_ids = tokenizer.encode(prompt, max_length=length - 4, truncation=True)
                short_prompt = tokenizer.decode(prompt_ids)
                stream_request = interface.GenerateStreamRequest(
                    inputs=short_prompt,
                    parameters=parameters,
                )
                ftrs: list[futures.Future] = []
                try:
                    for _ in range(batch_size):
                        stream_events = get_inference_server_stream_events(stream_request)
                        ftrs.append(executor.submit(list, stream_events))
                    for ftr in ftrs:
                        for stream_response in ftr.result():
                            if stream_response.is_error:
                                logger.error(f"Error from inference server: {stream_response.error}")
                                raise OOMError()
                except Exception:
                    logger.exception("OOM")
                    try:
                        for ftr in ftrs:
                            ftr.cancel()
                    except Exception:
                        pass
                    raise OOMError()
        except OOMError:
            batch_size = batch_size - 1
        logger.warning(f"Batch size: {batch_size}")

    logger.warning("OOM test complete")
    logger.warning(f"Max length: {length}")
    logger.warning(f"Batch size: {batch_size}")
