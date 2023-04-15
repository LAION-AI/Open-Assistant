import gzip
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, TextIO

from oasst_data.schemas import ExportMessageNode, ExportMessageTree


def default_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def open_jsonl_write(file_name: str | Path) -> TextIO:
    file_name = Path(file_name)
    if file_name.suffix == ".gz":
        return gzip.open(str(file_name), mode="wt", encoding="UTF-8")
    else:
        return file_name.open("w", encoding="UTF-8")


def write_tree(
    file: TextIO,
    tree: ExportMessageTree,
    exclude_none: bool = False,
) -> None:
    json.dump(tree.dict(exclude_none=exclude_none), file, default=default_serializer)
    file.write("\n")


def write_message_trees(
    output_file_name: str | Path,
    trees: Iterable[ExportMessageTree],
    exclude_none: bool,
) -> None:
    with open_jsonl_write(output_file_name) as file:
        # write one tree per line
        for tree in trees:
            write_tree(file, tree)


def write_message(
    file: TextIO,
    message: ExportMessageNode,
    exclude_none: bool = False,
) -> None:
    message = message.copy(deep=False, exclude={"replies"})
    json.dump(
        message.dict(exclude_none=exclude_none),
        file,
        default=default_serializer,
    )
    file.write("\n")


def write_messages(
    output_file_name: str | Path,
    messages: Iterable[ExportMessageNode],
    exclude_none: bool,
) -> None:
    with open_jsonl_write(output_file_name) as file:
        # write one message per line
        for message in messages:
            write_message(file, message, exclude_none)
