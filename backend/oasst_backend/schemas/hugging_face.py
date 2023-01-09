from pydantic import BaseModel


class ToxicityClassification(BaseModel):
    label: str
    score: float
