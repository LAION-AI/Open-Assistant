import pydantic


class CreateWorkerRequest(pydantic.BaseModel):
    name: str
