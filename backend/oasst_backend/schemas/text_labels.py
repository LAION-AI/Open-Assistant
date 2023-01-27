from oasst_shared.schemas.protocol import LabelDescription
from pydantic import BaseModel


class ValidLabelsResponse(BaseModel):
    valid_labels: list[LabelDescription]
