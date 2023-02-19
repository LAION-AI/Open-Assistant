import datetime
import enum
import random
from typing import Literal

import pydantic

INFERENCE_PROTOCOL_VERSION = "1"
DEFAULT_MODEL_NAME = "distilgpt2"


def compat_hash(*, model_name: str) -> str:
    return f"{model_name}"


class WorkerConfig(pydantic.BaseModel):
    model_name: str = DEFAULT_MODEL_NAME

    @property
    def compat_hash(self) -> str:
        return compat_hash(model_name=self.model_name)


class WorkParameters(pydantic.BaseModel):
    model_name: str = DEFAULT_MODEL_NAME
    max_new_tokens: int = 100
    do_sample: bool = True
    top_k: int = 50
    top_p: float = 0.9
    temperature: float = 1.0
    repetition_penalty: float | None = None
    seed: int = pydantic.Field(default_factory=lambda: random.randint(0, 0xFFFF_FFFF_FFFF_FFFF - 1))


class MessageState(str, enum.Enum):
    manual = "manual"
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    aborted_by_worker = "aborted_by_worker"


class MessageRead(pydantic.BaseModel):
    id: str
    content: str | None
    role: Literal["prompter", "assistant"]
    state: MessageState

    @property
    def is_assistant(self) -> bool:
        return self.role == "assistant"


class Thread(pydantic.BaseModel):
    messages: list[MessageRead]


class WorkRequest(pydantic.BaseModel):
    thread: Thread = pydantic.Field(..., repr=False)
    created_at: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.utcnow)
    parameters: WorkParameters = pydantic.Field(default_factory=WorkParameters)


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
    error: str | None = None
