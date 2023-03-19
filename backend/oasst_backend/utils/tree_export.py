from __future__ import annotations

import contextlib
import gzip
import hashlib
import json
import sys
import uuid
from collections import defaultdict
from typing import Iterable, Optional, TextIO

from fastapi.encoders import jsonable_encoder
from oasst_backend.models import Message
from oasst_backend.models.message_tree_state import State as TreeState
from oasst_data import (
    ExportMessageEvent,
    ExportMessageEventEmoji,
    ExportMessageEventRanking,
    ExportMessageEventRating,
    ExportMessageNode,
    ExportMessageTree,
    LabelValues,
)


def sha256_hash(key: str, seed: int) -> str:
    return hashlib.sha256(f"{key}{seed}".encode("UTF-8")).hexdigest()


class Anonymizer:
    def __init__(self, seed, value_generator=lambda key, seed: sha256_hash(key, seed)):
        self._map = {}
        self._values = set()
        self._seed = seed
        self._gen = value_generator

    def __getitem__(self, key):
        if key not in self._map:
            new_value = self._gen(key, self._seed)
            if new_value in self._values:
                raise ValueError("Generated value already exists. Try a different seed or value generator.")
            self._map[key] = new_value
            self._values.add(new_value)
        return self._map[key]

    def anonymize(self, collection: str, key: str | None) -> str | None:
        if key is None:
            return None
        return self[f"{collection}:{key}"]


def prepare_export_message_node(
    message: Message,
    labels: Optional[LabelValues] = None,
    anonymizer: Anonymizer | None = None,
    events: dict[str, list[ExportMessageEvent]] | None = None,
) -> ExportMessageNode:
    message_id = str(message.id)
    parent_id = str(message.parent_id) if message.parent_id else None
    user_id = str(message.user_id) if message.user_id else None
    if anonymizer is not None:
        message_id = anonymizer.anonymize("message", message_id)
        parent_id = anonymizer.anonymize("message", parent_id)
        user_id = anonymizer.anonymize("user", user_id)
        if events is not None:
            for event_key, event_values in events.items():
                for event in event_values:
                    match event_key:
                        case "emoji":
                            event: ExportMessageEventEmoji = event
                            if event.user_id is not None:
                                event.user_id = anonymizer.anonymize("user", event.user_id)
                        case "rating":
                            event: ExportMessageEventRating = event
                            if event.user_id is not None:
                                event.user_id = anonymizer.anonymize("user", event.user_id)
                        case "ranking":
                            event: ExportMessageEventRanking = event
                            if event.user_id is not None:
                                event.user_id = anonymizer.anonymize("user", event.user_id)
                            event.ranked_message_ids = [
                                anonymizer.anonymize("message", m) for m in event.ranked_message_ids
                            ]
                            if event.ranking_parent_id is not None:
                                event.ranking_parent_id = anonymizer.anonymize("message", event.ranking_parent_id)
                            if event.message_tree_id is not None:
                                event.message_tree_id = anonymizer.anonymize("message_tree", event.message_tree_id)
                        case _:
                            raise ValueError(f"Unknown event type {event_key}")
    assert message_id is not None
    return ExportMessageNode(
        message_id=message_id,
        parent_id=parent_id,
        user_id=user_id,
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
        events=events,
    )


def build_export_tree(
    message_tree_id: uuid.UUID,
    message_tree_state: TreeState,
    messages: list[Message],
    labels: Optional[dict[uuid.UUID, LabelValues]] = None,
    anonymizer: Anonymizer | None = None,
    events: dict[uuid.UUID, dict[str, list[ExportMessageEvent]]] | None = None,
) -> ExportMessageTree:
    export_messages = [
        prepare_export_message_node(
            m, (labels.get(m.id) if labels else None), anonymizer=anonymizer, events=events.get(m.id)
        )
        for m in messages
    ]

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
    labels: Optional[dict[uuid.UUID, LabelValues]] = None,
    anonymizer: Anonymizer | None = None,
    events: dict[uuid.UUID, dict[str, list[ExportMessageEvent]]] | None = None,
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
            export_message = prepare_export_message_node(
                m, (labels.get(m.id) if labels else None), anonymizer=anonymizer, events=events.get(m.id)
            )

            file_data = jsonable_encoder(export_message, exclude_none=True)
            json.dump(file_data, f)
            f.write("\n")
