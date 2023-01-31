from __future__ import annotations

import gzip
import json
from collections import defaultdict
from typing import Optional, TextIO

from fastapi.encoders import jsonable_encoder
from oasst_backend.models import Message
from pydantic import BaseModel


class ExportMessageNode(BaseModel):
    message_id: str
    parent_id: str | None
    text: str
    role: str
    lang: str | None
    review_count: int | None
    rank: int | None
    synthetic: bool | None
    model_name: str | None
    emojis: dict[str, int] | None
    replies: list[ExportMessageNode] | None

    @staticmethod
    def prep_message_export(message: Message) -> ExportMessageNode:
        return ExportMessageNode(
            message_id=str(message.id),
            parent_id=str(message.parent_id) if message.parent_id else None,
            text=str(message.payload.payload.text),
            role=message.role,
            lang=message.lang,
            review_count=message.review_count,
            synthetic=message.synthetic,
            model_name=message.model_name,
            emojis=message.emojis,
            rank=message.rank,
        )


class ExportMessageTree(BaseModel):
    message_tree_id: str
    prompt: Optional[ExportMessageNode]


def build_export_tree(message_tree_id: str, messages: list[Message]) -> ExportMessageTree:
    export_messages = [ExportMessageNode.prep_message_export(m) for m in messages]

    messages_by_parent = defaultdict(list)
    for message in export_messages:
        messages_by_parent[message.parent_id].append(message)

    def assign_replies(node: ExportMessageNode) -> ExportMessageNode:
        node.replies = messages_by_parent[node.message_id]
        node.replies.sort(key=lambda x: x.rank if x.rank is not None else float("inf"))
        for child in node.replies:
            assign_replies(child)
        return node

    prompt = assign_replies(messages_by_parent[None][0])
    return ExportMessageTree(message_tree_id=str(message_tree_id), prompt=prompt)


def write_trees_to_file(file, trees: list[ExportMessageTree], use_compression: bool = True) -> None:

    out_buff: TextIO
    if use_compression:
        out_buff = gzip.open(file, "wt", encoding="UTF-8")
    else:
        out_buff = open(file, "wt", encoding="UTF-8")

    with out_buff as f:
        for tree in trees:
            file_data = jsonable_encoder(tree)
            json.dump(file_data, f)
            f.write("\n")
