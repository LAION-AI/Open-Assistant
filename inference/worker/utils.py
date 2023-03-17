import collections
import random
import threading
import time
from typing import Iterable, Literal

import interface
import lorem
import requests
import websocket
from loguru import logger
from oasst_shared.schemas import inference


class TokenBuffer:
    def __init__(self, stop_sequences: list[str]) -> None:
        self.stop_sequences = stop_sequences
        self.longest_stop_len = max((len(stop) for stop in stop_sequences), default=0)
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
            while self.tokens:
                end_sequence = self.tokens.pop().text + end_sequence
                if end_sequence in self.stop_sequences:
                    break
            yield from self.tokens
        else:
            yield from self.tokens


def wait_for_inference_server(inference_server_url: str, timeout: int = 600):
    health_url = f"{inference_server_url}/health"
    time_limit = time.time() + timeout
    while True:
        try:
            response = requests.get(health_url)
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


def lorem_events(seed):
    sentence = lorem.sentence()
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
            seed=seed,
        ),
    )


ws_lock = threading.Lock()


def send_response(
    ws: websocket.WebSocket,
    repsonse: inference.WorkerResponse | inference.WorkerConfig,
):
    msg = repsonse.json()
    with ws_lock:
        ws.send(msg)
