from __future__ import annotations

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
    not_rankable: Optional[bool]  # all options flawed, factually incorrect or unacceptable


class ExportMessageNode(BaseModel):
    message_id: str
    parent_id: str | None
    user_id: str | None
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


class ExportMessageTree(BaseModel):
    message_tree_id: str
    tree_state: Optional[str]
    prompt: Optional[ExportMessageNode]
