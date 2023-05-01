import re
import threading
from concurrent import futures

import chat_chain
import interface
import requests
import sseclient
import transformers
import utils
import websocket
from chat_chain_prompts import ASSISTANT_PREFIX, END_SEQ, OBSERVATION_SEQ, START_SEQ, THOUGHT_SEQ
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
    # make room for prompter prefix
    if V2_PROMPTER_PREFIX not in prompt:
        max_input_length = max_input_length - 1

    max_total_tokens = worker_config.model_config.max_total_length
    if len(ids) > max_input_length:
        logger.warning(f"Prompt too long, left-truncating to {max_input_length} tokens")
        ids = ids[-(max_input_length - 1) :]
        with tokenizer_lock:
            prompt = tokenizer.decode(ids)
            # If there is no prompter prefix, due to truncation, add it back.
            if V2_PROMPTER_PREFIX not in prompt:
                prompt = V2_PROMPTER_PREFIX + prompt

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


def prepare_safe_prompt(prompt: str, label: str, rots: str) -> str:
    pre_prompt = f"Answer the following request with {label} as responsible chatbot that believes that {rots}: "
    input_list = prompt.split(V2_PROMPTER_PREFIX)
    input_list[-1] = pre_prompt + input_list[-1]
    return V2_PROMPTER_PREFIX.join(input_list)


def is_safety_triggered(safety_label: str, safety_level: int) -> bool:
    return ("caution" in safety_label and safety_level > 1) or ("intervention" in safety_label and safety_level > 0)


def parse_safety_response(safety_opinion: str) -> tuple[str, str]:
    safety_opinion = re.sub(r"<pad>|</s>", "", safety_opinion).split("<sep>")
    label, rots = safety_opinion[0], "and".join([x.strip(".") for x in safety_opinion[1:]])
    label = label.replace("<pad>", "").strip()
    return label, rots


def handle_work_request(
    ws: websocket.WebSocket,
    tokenizer: transformers.PreTrainedTokenizer,
    work_request: inference.WorkRequest,
    worker_config: inference.WorkerConfig,
):
    parameters = interface.GenerateStreamParameters.from_work_parameters(work_request.parameters)
    prompt = ""
    used_plugin = None

    # Check if any plugin is enabled, if so, use it.
    for plugin in parameters.plugins:
        if plugin.enabled:
            prompt, used_plugin = chat_chain.handle_conversation(work_request, worker_config, parameters, tokenizer)
            # When using plugins, and final prompt being truncated due to the input
            # length limit, LLaMA llm has tendency to leak internal promptings,
            # and generate undesirable continuations, so here we will be adding
            # some plugin keywords/sequences to the stop sequences to try preventing it
            parameters.stop.extend([END_SEQ, START_SEQ, THOUGHT_SEQ, ASSISTANT_PREFIX])
            break

    # If no plugin was "used", use the default prompt generation.
    if not used_plugin:
        prompt, parameters = make_prompt_and_parameters(tokenizer=tokenizer, work_request=work_request)

    logger.debug(f"Prompt: {prompt}")

    model_config = worker_config.model_config

    # Only send safety request if work request safety level is not 0
    if settings.enable_safety and work_request.safety_parameters.level:
        safety_request = inference.SafetyRequest(inputs=prompt, parameters=work_request.safety_parameters)
        safety_response = get_safety_server_response(safety_request)
        safety_label, safety_rots = parse_safety_response(safety_response.outputs)

        if is_safety_triggered(safety_label, work_request.safety_parameters.level):
            prompt = prepare_safe_prompt(prompt, safety_label, safety_rots)

            utils.send_response(
                ws,
                inference.SafePromptResponse(
                    request_id=work_request.id,
                    safe_prompt=prompt,
                    safety_parameters=work_request.safety_parameters,
                    safety_label=safety_label,
                    safety_rots=safety_rots,
                ),
            )

            logger.debug(f"Safe prompt: {prompt}")

    stream_response = None
    token_buffer = utils.TokenBuffer(stop_sequences=parameters.stop)
    if model_config.is_lorem:
        stream_events = utils.lorem_events(parameters.seed)
    else:
        prompt = truncate_prompt(tokenizer, worker_config, parameters, prompt)
        stream_request = interface.GenerateStreamRequest(
            inputs=prompt,
            parameters=parameters,
        )
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
            try:
                with tokenizer_lock:
                    text = tokenizer.decode(generated_ids, skip_special_tokens=True)
                new_text = text[len(decoded_text) :]
                if not decoded_text:
                    new_text = new_text.lstrip()
            except Exception:
                text = decoded_text
                new_text = ""
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
        # Get the generated text up to the first occurrence of any of:
        # START_SEQ, END_SEQ, ASSISTANT_PREFIX, THOUGHT_SEQ, OBSERVATION_SEQ
        end_seq_index = min(
            [
                stream_response.generated_text.find(seq)
                for seq in [START_SEQ, END_SEQ, ASSISTANT_PREFIX, THOUGHT_SEQ, OBSERVATION_SEQ]
                if seq in stream_response.generated_text
            ]
            + [len(stream_response.generated_text)]
        )
        if end_seq_index != -1 and used_plugin is not None:
            stream_response.generated_text = stream_response.generated_text[:end_seq_index]

    logger.info(f"Done. {stream_response=}")
    utils.send_response(
        ws,
        inference.GeneratedTextResponse(
            request_id=work_request.id,
            text=stream_response.generated_text,
            finish_reason=stream_response.details.finish_reason,
            metrics=inference.WorkerMetricsInfo(),
            used_plugin=used_plugin,
        ),
    )
    logger.debug("Work complete. Waiting for more work...")


def get_safety_server_response(request: inference.SafetyRequest) -> inference.SafetyResponse:
    http = utils.HttpClient(base_url=settings.safety_server_url)
    response = http.post("/safety", json=request.dict())
    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.exception("Failed to get response from safety server")
        logger.error(f"Response: {response.text}")
        raise
    return inference.SafetyResponse(**response.json())


def get_inference_server_stream_events(request: interface.GenerateStreamRequest):
    http = utils.HttpClient(
        base_url=settings.inference_server_url,
        basic_auth_username=settings.basic_auth_username,
        basic_auth_password=settings.basic_auth_password,
    )
    response = http.post(
        "/generate_stream",
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
        if event.event == "error":
            logger.error(f"Error from inference server: {event.data}")
            yield interface.GenerateStreamResponse(error=event.data)
            raise RuntimeError(f"Error from inference server: {event.data}")
        if event.event == "ping":
            continue
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
