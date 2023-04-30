import collections
import random
import threading
import time
from typing import Iterable, Literal

import interface
import lorem
import pydantic
import requests
import websocket
from loguru import logger
from oasst_shared.schemas import inference


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
    repsonse: inference.WorkerResponse | inference.WorkerInfo,
):
    msg = repsonse.json()
    with ws_lock:
        ws.send(msg)


class HttpClient(pydantic.BaseModel):
    base_url: str
    basic_auth_username: str | None = None
    basic_auth_password: str | None = None

    @property
    def auth(self):
        if self.basic_auth_username and self.basic_auth_password:
            return (self.basic_auth_username, self.basic_auth_password)
        else:
            return None

    def get(self, path: str, **kwargs):
        return requests.get(self.base_url + path, auth=self.auth, **kwargs)

    def post(self, path: str, **kwargs):
        return requests.post(self.base_url + path, auth=self.auth, **kwargs)
