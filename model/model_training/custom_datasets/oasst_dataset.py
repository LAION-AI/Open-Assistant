from pathlib import Path
from typing import Literal, Optional

from custom_datasets.formatting import format_pair, format_reply
from oasst_data import ExportMessageNode, load_trees, visit_threads_depth_first
from torch import Generator
from torch.utils.data import Dataset, random_split


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
    manual_seed: int = 287631038922,
    data_path: str | Path = None,
    mode: Literal["sft", "rm"] = "sft",
) -> tuple[ListDataset, ListDataset]:
    if mode not in ["sft", "rm"]:
        raise ValueError(f"Unknown dataset mode: {mode}")

    lang_codes = lang.split(",")

    generator = Generator()
    generator.manual_seed(manual_seed)

    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    if not input_file_path.is_absolute() and data_path:
        if not isinstance(data_path, Path):
            data_path = Path(data_path)
        input_file_path = data_path / input_file_path

    threads_per_tree = []
    for tree in load_trees(input_file_path):
        if tree.tree_state != "ready_for_export" or not tree.prompt.review_result or tree.prompt.lang not in lang_codes:
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
            if len(thread) <= 1 or not thread_filter(thread):
                return False
            if mode == "sft":
                return not thread[-1].replies and (
                    thread[-1].role == "assistant"
                )  # or thread[-2].replies[0] == thread[-1])
            else:  # mode == "rm"
                return thread[-1].role == "prompter" and len([r for r in thread[-1].replies if r.rank is not None]) > 1

        visit_threads_depth_first(tree.prompt, visitor=threads.append, predicate=leaf_filter)
        # for t in threads:
        #     if mode == "sft":
        #         if t[-1].role == "prompter":
        #             t.pop()

        threads_per_tree.append(threads)

    def process_thread(thread):
        if mode == "sft":
            return format_pair([m.text for m in thread])
        else:  # mode == "rm"
            prefix = format_pair([m.text for m in thread])
            replies = [r for r in thread[-1].replies if r.role == "assistant" and r.rank is not None]
            replies = sorted(replies, key=lambda r: r.rank)
            replies = [format_reply(r.text) for r in replies]
            return (prefix, replies)

    # split on tree basis, messages from same tree must not end up in different splits
    trees = ListDataset(threads_per_tree)
    splits = random_split(trees, lengths=[1.0 - val_split, val_split], generator=generator)

    def flatten(ds: ListDataset) -> ListDataset:
        return ListDataset([process_thread(thread) for tree_threads in ds for thread in tree_threads])

    train = flatten(splits[0])
    val = flatten(splits[1])

    print(f"OASST data {str(input_file_path)}: {len(train)=}, {len(val)=}")

    return train, val
