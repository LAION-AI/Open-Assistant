import gzip
import json
from pathlib import Path
from typing import Callable, Iterable, Optional, TextIO

import pydantic
from datasets import Dataset

from .schemas import ExportMessageNode, ExportMessageTree


def open_jsonl_read(input_file_path: str | Path) -> TextIO:
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    if input_file_path.suffix == ".gz":
        return gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
    else:
        return input_file_path.open("r", encoding="UTF-8")


def read_oasst_obj(obj_dict: dict) -> ExportMessageTree | ExportMessageNode:
    # validate data
    if "message_id" in obj_dict:
        return pydantic.parse_obj_as(ExportMessageNode, obj_dict)
    elif "message_tree_id" in obj_dict:
        return pydantic.parse_obj_as(ExportMessageTree, obj_dict)

    raise RuntimeError("Unknown object in jsonl file")


def read_oasst_jsonl(
    input_file_path: str | Path,
) -> Iterable[ExportMessageTree | ExportMessageNode]:
    with open_jsonl_read(input_file_path) as file_in:
        # read one object per line
        for line in file_in:
            dict_tree = json.loads(line)
            yield read_oasst_obj(dict_tree)


def read_oasst_dict_tree_hf_dataset(hf_dataset: Dataset) -> list[ExportMessageTree]:
    rows_by_id: dict[str, dict] = {}
    for row in hf_dataset:
        emojis = row.get("emojis")
        if emojis:
            row["emojis"] = dict(zip(emojis["name"], emojis["count"]))
        labels = row.get("labels")
        if labels:
            row["labels"] = {
                name: {"value": value, "count": count}
                for name, value, count in zip(
                    labels["name"], labels["value"], labels["count"]
                )
            }
        rows_by_id[row["message_id"]] = row
    raw_trees: list[dict] = []
    for row in rows_by_id.values():
        parent_id: str | None = row["parent_id"]
        if parent_id is None:
            raw_trees.append(
                {
                    "message_tree_id": row["message_id"],
                    "tree_state": row["tree_state"],
                    "prompt": row,
                }
            )
        else:
            parent = rows_by_id[parent_id]
            if "replies" not in parent:
                parent["replies"] = []
            parent["replies"].append(row)
        row.pop("message_tree_id", None)
        row.pop("tree_state", None)

    trees = [read_oasst_obj(t) for t in raw_trees]
    return trees


def read_message_trees(input_file_path: str | Path) -> Iterable[ExportMessageTree]:
    for x in read_oasst_jsonl(input_file_path):
        assert isinstance(x, ExportMessageTree)
        yield x


def read_message_tree_list(
    input_file_path: str | Path,
    filter: Optional[Callable[[ExportMessageTree], bool]] = None,
) -> list[ExportMessageTree]:
    return [t for t in read_message_trees(input_file_path) if not filter or filter(t)]


def read_messages(input_file_path: str | Path) -> Iterable[ExportMessageNode]:
    for x in read_oasst_jsonl(input_file_path):
        assert isinstance(x, ExportMessageNode)
        yield x


def read_message_list(
    input_file_path: str | Path,
    filter: Optional[Callable[[ExportMessageNode], bool]] = None,
) -> list[ExportMessageNode]:
    return [t for t in read_messages(input_file_path) if not filter or filter(t)]
