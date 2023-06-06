import collections
import random
import threading
import time
from typing import Iterable, Literal

import interface
import lorem
import pydantic
import requests
import sseclient
import transformers
import websocket
from chat_chain_prompts import V2_PROMPTER_PREFIX
from loguru import logger
from oasst_shared.schemas import inference
from settings import settings

shared_tokenizer_lock = threading.Lock()


class TokenBuffer:
    def __init__(self, stop_sequences: list[str]) -> None:
        self.stop_sequences = stop_sequences
        self.longest_stop_len = max((len(stop) for stop in stop_sequences), default=1)
        self.tokens = collections.deque()
        self.token_lens = collections.deque()
        self.total_len = 0

    def add(self, token: interface.Token):
        self.tokens.append(token)
        self.token_lens.append(len(token))
        self.total_len += len(token)
        while True:
            if not self.tokens:
                break
            head_len = self.token_lens[0]
            if self.total_len - head_len >= self.longest_stop_len:
                token = self.tokens.popleft()
                self.token_lens.popleft()
                self.total_len -= head_len
                yield token
            else:
                break

    def finish(self, reason: Literal["length", "eos_token", "stop_sequence"]) -> Iterable[interface.Token]:
        if reason == "stop_sequence":
            end_sequence = ""
            end_tokens = []
            while self.tokens:
                token = self.tokens.pop()
                end_tokens.append(token)
                end_sequence = token.text + end_sequence
                if end_sequence in self.stop_sequences:
                    break
            else:
                self.tokens.extend(reversed(end_tokens))
            yield from self.tokens
        elif reason == "eos_token":
            if self.tokens:
                self.tokens.pop()
            yield from self.tokens
        else:
            yield from self.tokens


def get_max_input_length(worker_config: inference.WorkerConfig, plugin_used: bool):
    max_input_length = worker_config.model_config.max_input_length
    if plugin_used:
        max_input_length = max_input_length - 1
    return max_input_length


def truncate_prompt(
    tokenizer: transformers.PreTrainedTokenizer,
    worker_config: inference.WorkerConfig,
    parameters: interface.GenerateStreamParameters,
    prompt: str,
    plugin_used: bool,
):
    with shared_tokenizer_lock:
        ids = tokenizer.encode(prompt)

    max_input_length = get_max_input_length(worker_config, plugin_used)

    if len(ids) > max_input_length:
        logger.debug(f"Prompt too long, left-truncating to {max_input_length} tokens")
        ids = ids[-(max_input_length - 1) :]

        with shared_tokenizer_lock:
            prompt = tokenizer.decode(ids)

            if V2_PROMPTER_PREFIX not in prompt:
                prompt = V2_PROMPTER_PREFIX + prompt
                ids = tokenizer.encode(V2_PROMPTER_PREFIX) + ids

    max_total_tokens = worker_config.model_config.max_total_length
    input_length = len(ids)
    spare = max_total_tokens - input_length - 1

    if not parameters.max_new_tokens:
        parameters.max_new_tokens = spare
    elif parameters.max_new_tokens > spare:
        logger.debug(f"Max new tokens too high, reducing to {spare}")
        parameters.max_new_tokens = spare

    return prompt


def wait_for_inference_server(http: "HttpClient", timeout: int = 600):
    time_limit = time.time() + timeout
    while True:
        try:
            response = http.get("/health")
            response.raise_for_status()
        except (requests.HTTPError, requests.ConnectionError):
            if time.time() > time_limit:
                raise
            sleep_duration = random.uniform(0, 10)
            logger.warning(f"Inference server not ready. Retrying in {sleep_duration:.2f} seconds")
            time.sleep(sleep_duration)
        else:
            logger.info("Inference server is ready")
            break


def text_to_events(text: str, seed: int | None = None, pause: float = 0.0):
    tokens = text.split()
    for token in tokens[:-1]:
        yield interface.GenerateStreamResponse(
            token=interface.Token(
                text=token + " ",
                logprob=0.1,
                id=0,
            ),
        )
        if pause > 0:
            time.sleep(pause)
    yield interface.GenerateStreamResponse(
        token=interface.Token(
            text=tokens[-1],
            logprob=0.1,
            id=0,
        ),
        generated_text=text,
        details=interface.StreamDetails(
            finish_reason="length",
            generated_tokens=len(tokens),
            seed=seed,
        ),
    )


def lorem_events(seed):
    sentence = lorem.paragraph()
    yield from text_to_events(sentence, seed=seed, pause=0.2)


ws_lock = threading.Lock()


def send_response(
    ws: websocket.WebSocket,
    response: inference.WorkerResponse | inference.WorkerInfo,
):
    msg = response.json()
    with ws_lock:
        ws.send(msg)


class HttpClient(pydantic.BaseModel):
    base_url: str
    basic_auth_username: str | None = None
    basic_auth_password: str | None = None
    bearer_token: str | None = None

    @property
    def auth(self):
        if self.basic_auth_username and self.basic_auth_password:
            return self.basic_auth_username, self.basic_auth_password
        else:
            return None

    def _maybe_add_bearer_token(self, headers: dict[str, str] | None):
        if self.bearer_token:
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    def get(self, path: str, **kwargs):
        kwargs["headers"] = self._maybe_add_bearer_token(kwargs.get("headers"))
        return requests.get(self.base_url + path, auth=self.auth, **kwargs)

    def post(self, path: str, **kwargs):
        kwargs["headers"] = self._maybe_add_bearer_token(kwargs.get("headers"))
        return requests.post(self.base_url + path, auth=self.auth, **kwargs)


def get_inference_server_stream_events(request: interface.GenerateStreamRequest):
    http = HttpClient(
        base_url=settings.inference_server_url,
        basic_auth_username=settings.basic_auth_username,
        basic_auth_password=settings.basic_auth_password,
        bearer_token=settings.bearer_token,
    )
    response = http.post(
        settings.inference_server_route,
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
