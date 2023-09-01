import re
from concurrent import futures

import chat_chain
import interface
import requests
import transformers
import utils
import websocket
from chat_chain_prompts import (
    ASSISTANT_PREFIX,
    CUSTOM_INSTRUCTIONS_PREFIX,
    END_SEQ,
    OBSERVATION_SEQ,
    START_SEQ,
    THOUGHT_SEQ,
)
from loguru import logger
from oasst_shared.schemas import inference
from settings import settings
from utils import shared_tokenizer_lock, special_tokens


def make_prompt_and_parameters(
    tokenizer: transformers.PreTrainedTokenizer,
    work_request: inference.WorkRequest,
) -> tuple[str, interface.GenerateStreamParameters]:
    """Prepare a formatted prompt and stream generation parameters based on a work request."""
    if settings.oa_protocol_version != "v2":
        raise RuntimeError(f"Unsupported oa protocol version: {settings.oa_protocol_version}")

    eos_token = ""
    if special_tokens["end"]:
        eos_token = special_tokens["end"]
    elif hasattr(tokenizer, "eos_token"):
        eos_token = tokenizer.eos_token

    def _prepare_message(message: inference.MessageRead) -> str:
        prefix = special_tokens["assistant"] if message.is_assistant else special_tokens["prompter"]
        return prefix + message.content + eos_token

    # Construct prompt
    messages = [_prepare_message(message) for message in work_request.thread.messages]

    # Prepend system prompt and custom_instructions if it was specified in work parameters
    work_params = work_request.parameters
    if work_params.system_prompt or work_params.user_profile or work_params.user_response_instructions:
        pre_prompt = special_tokens["system"] + (work_params.system_prompt or "")

        if work_params.user_profile or work_params.user_response_instructions:
            pre_prompt = f"""{pre_prompt}\n{CUSTOM_INSTRUCTIONS_PREFIX.format(user_profile=work_params.user_profile or "", user_response_instructions=work_params.user_response_instructions or "")}"""

        pre_prompt = pre_prompt + eos_token
        messages = [pre_prompt] + messages

    # Stringify and append assistant prefix to signify start of generation
    prompt = "".join(messages) + special_tokens["assistant"]

    parameters = interface.GenerateStreamParameters.from_work_parameters(work_request.parameters)
    if settings.use_stop_sequences:
        parameters.stop = [
            special_tokens["prompter"],
            special_tokens["assistant"],
            special_tokens["system"],
        ]
        if eos_token:
            parameters.stop.append(eos_token)
    else:
        parameters.stop = []

    return prompt, parameters


def prepare_safe_prompt(prompt: str, label: str, rots: str) -> str:
    """Given a prompt, safety label, and safety rule of thumb, prepare a 'safe prompt' to replace the prompt."""
    pre_prompt = f"Answer the following request with {label} as responsible chatbot that believes that {rots}: "
    input_list = prompt.split(special_tokens["prompter"])
    input_list[-1] = pre_prompt + input_list[-1]
    return special_tokens["prompter"].join(input_list)


def is_safety_triggered(safety_label: str, safety_level: int) -> bool:
    """
    Determines whether to trigger the safe prompt based on the configured safety level and severity label from the
    safety classifier.
    """
    return ("caution" in safety_label and safety_level > 1) or ("intervention" in safety_label and safety_level > 0)


def parse_safety_response(safety_opinion: str) -> tuple[str, str]:
    """Parse the response from the safety model into a separate label and rule of thumb."""
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
    """Handle a work request from end-to-end. Handles plugins and safety if enabled."""
    parameters = interface.GenerateStreamParameters.from_work_parameters(work_request.parameters)
    prompt = ""
    used_plugin = None

    for plugin in parameters.plugins:
        if plugin.enabled:
            prompt, used_plugin = chat_chain.handle_conversation(work_request, worker_config, parameters, tokenizer, ws)
            # When using plugins and final prompt is truncated due to length limit
            # LLaMA has tendency to leak internal prompts and generate bad continuations
            # So we add keywords/sequences to the stop sequences to reduce this
            parameters.stop.extend([END_SEQ, START_SEQ, THOUGHT_SEQ, f"{ASSISTANT_PREFIX}:"])
            break

    if not used_plugin:
        prompt, parameters = make_prompt_and_parameters(tokenizer=tokenizer, work_request=work_request)

    logger.debug(f"Prompt: {prompt}")

    model_config = worker_config.model_config

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
        prompt = utils.truncate_prompt(tokenizer, worker_config, parameters, prompt, used_plugin is not None)
        stream_request = interface.GenerateStreamRequest(
            inputs=prompt,
            parameters=parameters,
        )
        stream_events = utils.get_inference_server_stream_events(stream_request)

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
                with shared_tokenizer_lock:
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
        # Helps with RLHF models using plugin prompts. Get generated text to first occurrence of:
        # START_SEQ, END_SEQ, ASSISTANT_PREFIX, THOUGHT_SEQ, OBSERVATION_SEQ
        end_seq_index = min(
            [
                stream_response.generated_text.find(seq)
                for seq in [START_SEQ, END_SEQ, f"{ASSISTANT_PREFIX}:", THOUGHT_SEQ, OBSERVATION_SEQ]
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
    """Query the safety server URL configured in the worker settings."""
    http = utils.HttpClient(base_url=settings.safety_server_url)
    response = http.post("/safety", json=request.dict())
    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.exception("Failed to get response from safety server")
        logger.error(f"Response: {response.text}")
        raise
    return inference.SafetyResponse(**response.json())


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
                stream_events = utils.get_inference_server_stream_events(stream_request)
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
                        stream_events = utils.get_inference_server_stream_events(stream_request)
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
