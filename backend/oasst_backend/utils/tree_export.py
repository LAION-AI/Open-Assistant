from __future__ import annotations
from collections import defaultdict
import gzip
import json
from typing import Dict, List, Optional, TextIO

from fastapi.encoders import jsonable_encoder
from loguru import logger
from oasst_backend.models import Message
from pydantic import BaseModel


class ExportMessageNode(BaseModel):
    message_id: str
    parent_id: Optional[str]
    text: Optional[str]
    role: str
    review_count: Optional[int]
    rank: Optional[int]
    replies: Optional[List[ExportMessageNode]]

    @classmethod
    def prep_message_export(cls, message: Message) -> ExportMessageNode:
        return cls(
            message_id=str(message.id),
            parent_id=str(message.parent_id),
            text=str(message.payload.payload.text),
            role=message.role,
            review_count=message.review_count,
            rank=message.rank,
        )


class ExportMessageTree(BaseModel):
    message_tree_id: str
    replies: Optional[ExportMessageNode]


def build_export_tree(message_tree_id: str, messages: List[Message]) -> ExportMessageTree:
    export_tree = ExportMessageTree(message_tree_id=str(message_tree_id))
    export_tree_data = [ExportMessageNode.prep_message_export(m) for m in messages]

    message_parents = defaultdict(list)
    for message in export_tree_data:
        message_parents[str(message.parent_id)].append(message)

    def build_tree(tree: Dict, parent: str, messages: List[Message]):
        children = message_parents[parent]
        tree.replies = children

        for idx, child in enumerate(tree.replies):
            build_tree(tree.replies[idx], child.message_id, messages)

    build_tree(export_tree, "None", export_tree_data)

    return export_tree


def write_trees_to_file(file, trees: List[ExportMessageTree], use_compression: bool = True) -> None:

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
