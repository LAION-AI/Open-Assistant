import pydantic


class CreateWorkerRequest(pydantic.BaseModel):
    name: str


class WorkerRead(pydantic.BaseModel):
    id: str
    name: str
    api_key: str
