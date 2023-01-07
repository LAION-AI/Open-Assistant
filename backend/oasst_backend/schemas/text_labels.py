from typing import Optional

from pydantic import BaseModel


class LabelOption(BaseModel):
    name: str
    display_text: str
    help_text: Optional[str]


class ValidLabelsResponse(BaseModel):
    valid_labels: list[LabelOption]
