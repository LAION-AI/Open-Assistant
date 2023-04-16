import gzip
import json
from pathlib import Path
from typing import Callable, Iterable, Optional, TextIO

import pydantic

from .schemas import ExportMessageNode, ExportMessageTree


def open_jsonl_read(input_file_path: str | Path) -> TextIO:
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    if input_file_path.suffix == ".gz":
        return gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
    else:
        return input_file_path.open("r", encoding="UTF-8")


def read_oasst_obj(line: str) -> ExportMessageTree | ExportMessageNode:
    dict_tree = json.loads(line)
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
            yield read_oasst_obj(line)


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
