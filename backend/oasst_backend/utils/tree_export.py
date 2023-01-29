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
    replies: list[ExportMessageNode] | None

    @classmethod
    def prep_message_export(cls, message: Message) -> ExportMessageNode:
        return cls(
            message_id=str(message.id),
            parent_id=str(message.parent_id) if message.parent_id else None,
            text=str(message.payload.payload.text),
            role=message.role,
            lang=message.lang,
            review_count=message.review_count,
            synthetic=message.synthetic,
            model_name=message.model_name,
            rank=message.rank,
        )


class ExportMessageTree(BaseModel):
    message_tree_id: str
    prompt: Optional[ExportMessageNode]


def build_export_tree(message_tree_id: str, messages: list[Message]) -> ExportMessageTree:
    export_tree = ExportMessageTree(message_tree_id=str(message_tree_id))
    export_tree_data = [ExportMessageNode.prep_message_export(m) for m in messages]

    message_parents = defaultdict(list)
    for message in export_tree_data:
        message_parents[message.parent_id].append(message)

    def build_tree(tree: dict, parent: Optional[str], messages: list[Message]):
        children = message_parents[parent]
        tree.replies = children

        for idx, child in enumerate(tree.replies):
            build_tree(tree.replies[idx], child.message_id, messages)

    build_tree(export_tree, None, export_tree_data)

    return export_tree


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
