import gzip
import json
from pathlib import Path
from typing import Callable, Iterable, Optional, TextIO

import pydantic
from datasets import load_dataset

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


def read_message_trees(input_file_path: str | Path) -> Iterable[ExportMessageTree]:
    for x in read_oasst_jsonl(input_file_path):
        assert isinstance(x, ExportMessageTree)
        yield x


def read_message_tree_list(
    input_file_path: str | Path,
    filter: Optional[Callable[[ExportMessageTree], bool]] = None,
) -> list[ExportMessageTree]:
    return [t for t in read_message_trees(input_file_path) if not filter or filter(t)]


def convert_hf_message(row: dict) -> None:
    emojis = row.get("emojis")
    if emojis:
        row["emojis"] = dict(zip(emojis["name"], emojis["count"]))
    labels = row.get("labels")
    if labels:
        row["labels"] = {
            name: {"value": value, "count": count}
            for name, value, count in zip(labels["name"], labels["value"], labels["count"])
        }


def read_messages(input_file_path: str | Path) -> Iterable[ExportMessageNode]:
    for x in read_oasst_jsonl(input_file_path):
        assert isinstance(x, ExportMessageNode)
        yield x


def read_message_list(
    input_file_path: str | Path,
    filter: Optional[Callable[[ExportMessageNode], bool]] = None,
) -> list[ExportMessageNode]:
    return [t for t in read_messages(input_file_path) if not filter or filter(t)]


def read_dataset_message_trees(
    hf_dataset_name: str = "OpenAssistant/oasst1",
    split: str = "train+validation",
) -> Iterable[ExportMessageTree]:
    dataset = load_dataset(hf_dataset_name, split=split)

    tree_dict: dict = None
    parents: list = None
    for row in dataset:
        convert_hf_message(row)
        if row["parent_id"] is None:
            if tree_dict:
                tree = read_oasst_obj(tree_dict)
                assert isinstance(tree, ExportMessageTree)
                yield tree

            tree_dict = {
                "message_tree_id": row["message_id"],
                "tree_state": row["tree_state"],
                "prompt": row,
            }
            parents = []
        else:
            while parents[-1]["message_id"] != row["parent_id"]:
                parents.pop()
            parent = parents[-1]
            if "replies" not in parent:
                parent["replies"] = []
            parent["replies"].append(row)

        row.pop("message_tree_id", None)
        row.pop("tree_state", None)
        parents.append(row)

    if tree_dict:
        tree = read_oasst_obj(tree_dict)
        assert isinstance(tree, ExportMessageTree)
        yield tree


def read_dataset_messages(
    hf_dataset_name: str = "OpenAssistant/oasst1",
    split: str = "train+validation",
) -> Iterable[ExportMessageNode]:
    dataset = load_dataset(hf_dataset_name, split=split)

    for row in dataset:
        convert_hf_message(row)
        message = read_oasst_obj(row)
        assert isinstance(message, ExportMessageNode)
        yield message
