import pydantic


class CreateWorkerRequest(pydantic.BaseModel):
    name: str
    trusted: bool = False


class WorkerRead(pydantic.BaseModel):
    id: str
    name: str
    api_key: str
    trusted: bool
