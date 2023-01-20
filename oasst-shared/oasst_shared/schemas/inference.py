import pydantic


class WorkerConfig(pydantic.BaseModel):
    model_name: str = "distilgpt2"


class WorkRequest(pydantic.BaseModel):
    stream_queue_id: str
    prompt: str = pydantic.Field(..., repr=False)
    model_name: str = "distilgpt2"
    max_length: int = 100
    seed: int = 42


class WorkResponsePacket(pydantic.BaseModel):
    token: str | None = None
    is_end: bool = False
