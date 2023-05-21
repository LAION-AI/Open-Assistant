import gzip
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional, TextIO

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


def read_oasst_obj(dict_tree: dict) -> ExportMessageTree | ExportMessageNode:
    # validate data
    if "message_id" in dict_tree:
        return pydantic.parse_obj_as(ExportMessageNode, dict_tree)
    elif "message_tree_id" in dict_tree:
        return pydantic.parse_obj_as(ExportMessageTree, dict_tree)

    raise RuntimeError("Unknown object in jsonl file")


def read_oasst_jsonl(input_file_path: str | Path) -> Iterable[ExportMessageTree | ExportMessageNode]:
    with open_jsonl_read(input_file_path) as file_in:
        # read one object per line
        for line in file_in:
            dict_tree = json.loads(line)
            yield read_oasst_obj(dict_tree)


def read_oasst_dict_tree_hf_dataset(hf_dataset: Dataset) -> Iterable[ExportMessageTree]:
    for x in rebuild_trees_from_hf_dataset(hf_dataset):
        assert isinstance(x, ExportMessageTree)
        yield x


def read_message_trees(input_file_path: str | Path) -> Iterable[ExportMessageTree]:
    for x in read_oasst_jsonl(input_file_path):
        assert isinstance(x, ExportMessageTree)
        yield x


def read_message_tree_list(
    input_file_path: str | Path, filter: Optional[Callable[[ExportMessageTree], bool]] = None
) -> list[ExportMessageTree]:
    return [t for t in read_message_trees(input_file_path) if not filter or filter(t)]


def read_messages(input_file_path: str | Path) -> Iterable[ExportMessageNode]:
    for x in read_oasst_jsonl(input_file_path):
        assert isinstance(x, ExportMessageNode)
        yield x


def read_message_list(
    input_file_path: str | Path, filter: Optional[Callable[[ExportMessageNode], bool]] = None
) -> list[ExportMessageNode]:
    return [t for t in read_messages(input_file_path) if not filter or filter(t)]


def rebuild_trees_from_hf_dataset(hf_dataset: Dataset):
    for row in hf_dataset.filter(lambda x: x["parent_id"] is None):
        new_dict_tree = {}
        dict_tree = rebuild_trees_recursively(hf_dataset, row)

        new_dict_tree["message_tree_id"] = dict_tree["message_tree_id"]
        new_dict_tree["tree_state"] = dict_tree["tree_state"]
        dict_tree.pop("parent_id", None)
        dict_tree.pop("message_tree_id", None)
        dict_tree.pop("tree_state", None)

        new_dict_tree["prompt"] = dict_tree

        yield read_oasst_obj(new_dict_tree)


def rebuild_trees_recursively(hf_dataset: Dataset, dict_tree: Dict):
    if dict_tree["parent_id"] is not None:
        dict_tree.pop("message_tree_id", None)
        dict_tree.pop("tree_state", None)

    replies = [
        rebuild_trees_recursively(hf_dataset, data)
        for data in hf_dataset.filter(lambda x: x["parent_id"] == dict_tree["message_id"])
    ]

    if len(replies) > 0:
        dict_tree["replies"] = replies

    return dict_tree
