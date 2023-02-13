import random
from typing import Literal

import pydantic

from . import protocol

INFERENCE_PROTOCOL_VERSION = "1"


def compat_hash(*, model_name: str) -> str:
    return f"{model_name}"


class WorkerConfig(pydantic.BaseModel):
    model_name: str = "distilgpt2"

    @property
    def compat_hash(self) -> str:
        return compat_hash(model_name=self.model_name)


class WorkRequest(pydantic.BaseModel):
    conversation: protocol.Conversation = pydantic.Field(..., repr=False)
    model_name: str = "distilgpt2"
    max_new_tokens: int = 100
    seed: int = pydantic.Field(default_factory=lambda: random.randint(0, 0xFFFF_FFFF_FFFF_FFFF - 1))
    do_sample: bool = True
    top_k: int = 50
    top_p: float = 0.9
    temperature: float = 1.0
    repetition_penalty: float | None = None


class TokenResponse(pydantic.BaseModel):
    text: str
    log_prob: float
    token_id: int


class GeneratedTextResponse(pydantic.BaseModel):
    text: str
    finish_reason: Literal["length", "eos_token", "stop_sequence"]


class WorkResponsePacket(pydantic.BaseModel):
    token: TokenResponse | None = None
    generated_text: GeneratedTextResponse | None = None
    is_end: bool = False
