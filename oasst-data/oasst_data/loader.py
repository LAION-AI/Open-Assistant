import gzip
import json
from pathlib import Path
from typing import Callable, Iterable, Optional

import pydantic

from .schemas import ExportMessageTree


def load_trees(input_file_path: str | Path) -> Iterable[ExportMessageTree]:
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    if input_file_path.suffix == ".gz":
        file_in = gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
    else:
        file_in = input_file_path.open("r", encoding="UTF-8")

    with file_in:
        # read one message tree per line
        for line in file_in:
            dict_tree = json.loads(line)

            # validate data
            yield pydantic.parse_obj_as(ExportMessageTree, dict_tree)


def load_tree_list(
    input_file_path: str | Path, filter: Optional[Callable[[ExportMessageTree], bool]] = None
) -> list[ExportMessageTree]:
    return [t for t in load_trees(input_file_path) if not filter or filter(t)]
