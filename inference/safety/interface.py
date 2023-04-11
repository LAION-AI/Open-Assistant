import pydantic

# TODO: make a shared interface between worker and safety instead of just duplicating the code


class SafetyParameters(pydantic.BaseModel):
    ...


class SafetyRequest(pydantic.BaseModel):
    inputs: str
    parameters: SafetyParameters


class SafetyResponse(pydantic.BaseModel):
    outputs: str
