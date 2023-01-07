from pydantic import BaseModel


class LabelOption(BaseModel):
    name: str
    description: str


class ValidLabelsResponse(BaseModel):
    valid_labels: list[LabelOption]
