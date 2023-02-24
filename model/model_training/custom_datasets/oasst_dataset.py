import gzip
import json
from pathlib import Path
from typing import Callable, Optional

import pydantic
from custom_datasets.formatting import format_pair
from oasst_shared.schemas.export import ExportMessageNode, ExportMessageTree
from torch import Generator, default_generator
from torch.utils.data import Dataset, random_split


def _visit_threads_depth_first(
    node: ExportMessageNode,
    visitor: Callable[[list[ExportMessageNode]], None],
    predicate: Optional[Callable[[list[ExportMessageNode]], bool]] = None,
    parents: list[ExportMessageNode] = None,
):
    parents = parents or []
    if not node:
        return
    thread = parents + [node]
    if predicate is None or predicate(thread):
        visitor(thread)
    if node.replies:
        parents = thread
        for c in node.replies:
            _visit_threads_depth_first(node=c, visitor=visitor, predicate=predicate, parents=parents)


class ListDataset(Dataset):
    def __init__(self, data: list):
        super().__init__()
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


def load_oasst_export(
    input_file_path: str | Path,
    val_split: float = 0.2,
    lang: str = "en",
    top_k: Optional[int] = None,
    generator: Optional[Generator] = default_generator,
    data_path: str | Path = None,
) -> tuple[ListDataset, ListDataset]:
    lang_codes = lang.split(",")

    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    if not input_file_path.is_absolute() and data_path:
        if not isinstance(data_path, Path):
            data_path = Path(data_path)
        input_file_path = data_path / input_file_path

    if input_file_path.suffix == ".gz":
        file_in = gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
    else:
        file_in = input_file_path.open("r", encoding="UTF-8")

    threads_per_tree = []

    with file_in:
        # read one message tree per line
        for line in file_in:
            dict_tree = json.loads(line)

            # validate data
            tree: ExportMessageTree = pydantic.parse_obj_as(ExportMessageTree, dict_tree)

            if (
                tree.tree_state != "ready_for_export"
                or not tree.prompt.review_result
                or tree.prompt.lang not in lang_codes
            ):
                continue

            # extract all threads up to last asssitant reply
            threads: list[list[ExportMessageNode]] = []

            def thread_filter(thread: list[ExportMessageNode]) -> bool:
                if any(m.deleted for m in thread):
                    return False

                if top_k is not None:
                    for i, m in enumerate(thread):
                        if m.role == "assistant":
                            if m.rank is None:
                                if len(thread[i - 1].replies) > 1:
                                    return False
                            elif m.rank >= top_k:
                                return False
                return True

            def leaf_filter(thread: list[ExportMessageNode]) -> bool:
                return (
                    len(thread) > 1
                    and not thread[-1].replies
                    and (thread[-1].role == "assistant" or thread[-2].replies[0] == thread[-1])
                    and thread_filter(thread)
                )

            _visit_threads_depth_first(tree.prompt, threads.append, leaf_filter)
            for t in threads:
                if t[-1].role == "prompter":
                    t.pop()

            threads_per_tree.append(threads)

    # split on tree basis, messages from same tree must not end up in different splits
    trees = ListDataset(threads_per_tree)
    splits = random_split(trees, lengths=[1.0 - val_split, val_split], generator=generator)

    def flatten(d: ListDataset) -> ListDataset:
        return ListDataset([format_pair([m.text for m in t]) for ts in d for t in ts])

    train = flatten(splits[0])
    val = flatten(splits[1])

    return train, val
