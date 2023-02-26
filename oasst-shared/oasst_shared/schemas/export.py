from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class LabelAvgValue(BaseModel):
    value: float | None
    count: int


LabelValues = dict[str, LabelAvgValue]


class ExportMessageNode(BaseModel):
    message_id: str
    parent_id: str | None
    text: str
    role: str
    lang: str | None
    review_count: int | None
    review_result: bool | None
    deleted: bool | None
    rank: int | None
    synthetic: bool | None
    model_name: str | None
    emojis: dict[str, int] | None
    replies: list[ExportMessageNode] | None
    labels: LabelValues | None


class ExportMessageTree(BaseModel):
    message_tree_id: str
    tree_state: Optional[str]
    prompt: Optional[ExportMessageNode]
