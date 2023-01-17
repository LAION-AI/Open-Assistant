import gzip
import json
from typing import List, Dict, Optional
from pydantic import BaseModel
from oasst_backend.models import Message
from loguru import logger
from fastapi.encoders import jsonable_encoder


class ExportMessageNode(BaseModel):
    message_id: str
    parent_id: Optional[str]
    text: Optional[str]
    role: str
    review_count: Optional[int]
    rank: Optional[int]
    replies: Optional[List["ExportMessageNode"]]

    @classmethod
    def prep_message_export(cls, message: Message) -> "ExportMessageNode":
        return cls(
            message_id=str(message.id),
            parent_id=str(message.parent_id),
            text=str(message.payload),
            role=message.role,
            review_count=message.review_count,
            rank=message.rank,
        )


class ExportMessageTree(BaseModel):
    replies: Optional[ExportMessageNode]
    message_tree_id: str


def build_export_tree(message_tree_id: str, messages: List[Message]) -> ExportMessageTree:
    export_tree = ExportMessageTree(message_tree_id=message_tree_id)
    export_tree_data = [ExportMessageNode.prep_message_export(m) for m in messages]

    def build_tree(tree: Dict, parent, messages):
        children = [m for m in messages if m.parent_id == parent]
        tree.replies = children

        for idx, child in enumerate(tree.replies):
            build_tree(tree.replies[idx], child.message_id, messages)

    build_tree(export_tree, "None", export_tree_data)

    return export_tree


def write_tree_to_file(file, tree: ExportMessageTree, use_compression: bool = True) -> None:

    if use_compression:
        with gzip.open(file, "wt+", encoding="UTF-8") as comp_f:
            file_data = jsonable_encoder(tree)
            json.dump(file_data, comp_f, indent=2)
    else:
        with open(file, "wt+", encoding="UTF-8") as f:
            file_data = jsonable_encoder(tree)
            json.dump(file_data, f, indent=2)
