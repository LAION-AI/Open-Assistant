from __future__ import annotations

import contextlib
import gzip
import json
import sys
from collections import defaultdict
from typing import Iterable, Optional, TextIO
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from oasst_backend.models import Message
from oasst_backend.models.message_tree_state import State as TreeState
from oasst_shared.schemas.export import ExportMessageNode, ExportMessageTree, LabelValues


def prepare_export_message_node(message: Message, labels: Optional[LabelValues] = None) -> ExportMessageNode:
    return ExportMessageNode(
        message_id=str(message.id),
        parent_id=str(message.parent_id) if message.parent_id else None,
        text=str(message.payload.payload.text),
        role=message.role,
        lang=message.lang,
        deleted=message.deleted,
        review_count=message.review_count,
        review_result=message.review_result if message.review_result or message.review_count > 2 else None,
        synthetic=message.synthetic,
        model_name=message.model_name,
        emojis=message.emojis,
        rank=message.rank,
        labels=labels,
    )


def build_export_tree(
    message_tree_id: UUID,
    message_tree_state: TreeState,
    messages: list[Message],
    labels: Optional[dict[UUID, LabelValues]] = None,
) -> ExportMessageTree:
    export_messages = [prepare_export_message_node(m, labels.get(m.id) if labels else None) for m in messages]

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
    return ExportMessageTree(message_tree_id=str(message_tree_id), tree_state=message_tree_state, prompt=prompt)


# see https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(filename: str = None) -> TextIO:
    if filename and filename != "-":
        fh = open(filename, "wt", encoding="UTF-8")
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def write_trees_to_file(filename: str | None, trees: list[ExportMessageTree], use_compression: bool = True) -> None:
    out_buff: TextIO

    if use_compression:
        if not filename:
            raise RuntimeError("File name must be specified when using compression.")
        out_buff = gzip.open(filename, "wt", encoding="UTF-8")
    else:
        out_buff = smart_open(filename)

    with out_buff as f:
        for tree in trees:
            file_data = jsonable_encoder(tree, exclude_none=True)
            json.dump(file_data, f)
            f.write("\n")


def write_messages_to_file(
    filename: str | None,
    messages: Iterable[Message],
    use_compression: bool = True,
    labels: Optional[dict[UUID, LabelValues]] = None,
) -> None:
    out_buff: TextIO

    if use_compression:
        if not filename:
            raise RuntimeError("File name must be specified when using compression.")
        out_buff = gzip.open(filename, "wt", encoding="UTF-8")
    else:
        out_buff = smart_open(filename)

    with out_buff as f:
        for m in messages:
            export_message = prepare_export_message_node(m, labels.get(m.id) if labels else None)

            file_data = jsonable_encoder(export_message, exclude_none=True)
            json.dump(file_data, f)
            f.write("\n")
