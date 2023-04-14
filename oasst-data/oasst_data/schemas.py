from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class LabelAvgValue(BaseModel):
    value: float | None
    count: int


LabelValues = dict[str, LabelAvgValue]


class ExportMessageEvent(BaseModel):
    type: str
    user_id: str | None


class ExportMessageEventEmoji(ExportMessageEvent):
    type: Literal["emoji"] = "emoji"
    emoji: str


class ExportMessageEventRating(ExportMessageEvent):
    type: Literal["rating"] = "rating"
    rating: str


class ExportMessageEventRanking(ExportMessageEvent):
    type: Literal["ranking"] = "ranking"
    ranking: list[int]
    ranked_message_ids: list[str]
    ranking_parent_id: Optional[str]
    message_tree_id: Optional[str]
    not_rankable: Optional[bool]  # flawed, factually incorrect or unacceptable


class DetoxifyRating(BaseModel):
    toxicity: float
    severe_toxicity: float
    obscene: float
    identity_attack: float
    insult: float
    threat: float
    sexual_explicit: float


class ExportMessageNode(BaseModel):
    message_id: str
    parent_id: str | None
    user_id: str | None
    created_date: datetime | None
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
    events: dict[str, list[ExportMessageEvent]] | None
    detoxify: DetoxifyRating | None
    # the following fields are always None in message tree exports (see outer tree there)
    message_tree_id: str | None
    tree_state: str | None


class ExportMessageTree(BaseModel):
    message_tree_id: str
    tree_state: Optional[str]
    prompt: Optional[ExportMessageNode]
    origin: Optional[str]
