import random

import pydantic

from . import protocol


class WorkerConfig(pydantic.BaseModel):
    model_name: str = "distilgpt2"


class WorkRequest(pydantic.BaseModel):
    conversation: protocol.Conversation = pydantic.Field(..., repr=False)
    model_name: str = "distilgpt2"
    max_new_tokens: int = 100
    seed: int = pydantic.Field(default_factory=lambda: random.randint(0, 2**32 - 1))


class WorkResponsePacket(pydantic.BaseModel):
    token: str | None = None
    is_end: bool = False
