from pathlib import Path
from typing import Literal, Optional

from oasst_data import ExportMessageNode, read_message_trees, read_messages, visit_threads_depth_first
from torch import Generator
from torch.utils.data import Dataset, random_split

from .formatting import ATTRIBUTE_KEYS


class ListDataset(Dataset):
    def __init__(self, data: list):
        super().__init__()
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


def load_oasst_export_w_label(
    input_file_path: str | Path,
    input_label_path: str | Path,
    val_split: float = 0.2,
    lang: str = "en",
    top_k: Optional[int] = None,
    manual_seed: int = 287631038922,
    data_path: str | Path = None,
    mode: Literal["sft", "rm", "rl"] = "sft",
) -> tuple[ListDataset, ListDataset]:
    lang_codes = lang.split(",")

    generator = Generator()
    generator.manual_seed(manual_seed)

    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    if not input_file_path.is_absolute() and data_path:
        if not isinstance(data_path, Path):
            data_path = Path(data_path)
        input_file_path = data_path / input_file_path

    if not isinstance(input_label_path, Path):
        input_label_path = Path(input_label_path)
    if not input_label_path.is_absolute() and data_path:
        if not isinstance(data_path, Path):
            data_path = Path(data_path)
        input_label_path = data_path / input_label_path

    message_label = {}
    for msg in read_messages(input_label_path):
        attribute = {attr: msg.labels[attr].value for attr in ATTRIBUTE_KEYS if attr in msg.labels}
        if len(attribute) == len(ATTRIBUTE_KEYS):
            message_label[msg.message_id] = attribute

    threads_per_tree = []
    for tree in read_message_trees(input_file_path):
        if tree.tree_state != "ready_for_export" or not tree.prompt.review_result or tree.prompt.lang not in lang_codes:
            continue

        if mode in ("sft", "rm"):
            if tree.tree_state != "ready_for_export":
                continue
        elif mode == "rl":
            if tree.tree_state not in ("ready_for_export", "prompt_lottery_waiting"):
                continue

        # extract all threads up to last asssitant reply
        threads: list[list[ExportMessageNode]] = []

        def thread_filter(thread: list[ExportMessageNode]) -> bool:
            if any(m.deleted or m.synthetic for m in thread):
                return False

            if top_k is not None:
                for i, m in enumerate(thread):
                    if m.role == "assistant":
                        if m.rank is None:
                            if i > 0 and len(thread[i - 1].replies) > 1:
                                return False
                        elif m.rank >= top_k:
                            return False
            return True

        def leaf_filter(thread: list[ExportMessageNode]) -> bool:
            if mode == "sft":
                # in SFT mode `not thread[-1].replies` finds nodes without children (leaves).
                # We are interested in those which are role='assistant' but some trees don't end on assistant nodes
                # but have prompter leaves .. we want to use those trees too .. e.g. remove the last prompter message(s)
                # so that they end with assistant. The `thread[-2].replies[0] == thread[-1]` check makes sure that only
                # the FIRST prompter reply is added .. e.g. the parent does not appear multiple times and we can use
                # pop() to remove superfluous prompter leaf node later.
                return (
                    len(thread) > 1
                    and not thread[-1].replies
                    and (thread[-1].role == "assistant" or thread[-2].replies[0] == thread[-1])
                    and thread_filter(thread)
                )
            elif mode == "rm":
                # for reward models we use thread-fragments ending on prompter messages as prefix and
                # their (ranked) replies as possible continuations.
                return (
                    thread[-1].role == "prompter"
                    and len([r for r in thread[-1].replies if r.rank is not None]) > 1
                    and thread_filter(thread)
                )
            elif mode == "rl":
                # during rl we are interested in all possible prefixes ending in prompter messages
                return thread[-1].role == "prompter" and not any(m.deleted or m.synthetic for m in thread)

            raise RuntimeError()

        visit_threads_depth_first(tree.prompt, visitor=threads.append, predicate=leaf_filter)
        if mode == "sft":
            for t in threads:
                if t[-1].role == "prompter":
                    t.pop()

        threads_per_tree.append(threads)

    def process_thread(thread):
        if mode == "sft":
            return [m.text for m in thread]
        elif mode == "rm":
            prefix = [m.text for m in thread]
            replies = [r for r in thread[-1].replies if r.role == "assistant" and r.rank is not None]
            replies = sorted(replies, key=lambda r: r.rank)
            filtered_replies = []
            labels = []
            for r in replies:
                if r.message_id in message_label:
                    filtered_replies.append([r.text])
                    labels.append(message_label[r.message_id])
            return (prefix, filtered_replies, labels)
        elif mode == "rl":
            return ([m.text for m in thread],)

        raise RuntimeError()

    # split on tree basis, messages from same tree must not end up in different splits
    trees = ListDataset(threads_per_tree)
    splits = random_split(trees, lengths=[1.0 - val_split, val_split], generator=generator)

    def flatten(ds: ListDataset) -> ListDataset:
        flatten_msg = []
        for tree_threads in ds:
            for thread in tree_threads:
                msg = process_thread(thread)
                if mode == "rm":
                    if len(msg[-1]) > 1 and len(msg[-2]) > 1:
                        flatten_msg.append(msg)
                else:
                    flatten_msg.append(msg)
        return ListDataset(flatten_msg)

    train = flatten(splits[0])
    val = flatten(splits[1])

    print(f"OASST data {str(input_file_path)}: {len(train)=}, {len(val)=}")

    return train, val


def load_oasst_export(
    input_file_path: str | Path,
    val_split: float = 0.2,
    lang: str = "en",
    top_k: Optional[int] = None,
    manual_seed: int = 287631038922,
    data_path: str | Path = None,
    mode: Literal["sft", "rm", "rl"] = "sft",
) -> tuple[ListDataset, ListDataset]:
    if mode not in ("sft", "rm", "rl"):
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
    for tree in read_message_trees(input_file_path):
        if tree.tree_state != "ready_for_export" or not tree.prompt.review_result or tree.prompt.lang not in lang_codes:
            continue

        if mode in ("sft", "rm"):
            if tree.tree_state != "ready_for_export":
                continue
        elif mode == "rl":
            if tree.tree_state not in ("ready_for_export", "prompt_lottery_waiting"):
                continue

        # extract all threads up to last asssitant reply
        threads: list[list[ExportMessageNode]] = []

        def thread_filter(thread: list[ExportMessageNode]) -> bool:
            if any(m.deleted or m.synthetic for m in thread):
                return False

            if top_k is not None:
                for i, m in enumerate(thread):
                    if m.role == "assistant":
                        if m.rank is None:
                            if i > 0 and len(thread[i - 1].replies) > 1:
                                return False
                        elif m.rank >= top_k:
                            return False
            return True

        def leaf_filter(thread: list[ExportMessageNode]) -> bool:
            if mode == "sft":
                # in SFT mode `not thread[-1].replies` finds nodes without children (leaves).
                # We are interested in those which are role='assistant' but some trees don't end on assistant nodes
                # but have prompter leaves .. we want to use those trees too .. e.g. remove the last prompter message(s)
                # so that they end with assistant. The `thread[-2].replies[0] == thread[-1]` check makes sure that only
                # the FIRST prompter reply is added .. e.g. the parent does not appear multiple times and we can use
                # pop() to remove superfluous prompter leaf node later.
                return (
                    len(thread) > 1
                    and not thread[-1].replies
                    and (thread[-1].role == "assistant" or thread[-2].replies[0] == thread[-1])
                    and thread_filter(thread)
                )
            elif mode == "rm":
                # for reward models we use thread-fragments ending on prompter messages as prefix and
                # their (ranked) replies as possible continuations.
                return (
                    thread[-1].role == "prompter"
                    and len([r for r in thread[-1].replies if r.rank is not None]) > 1
                    and thread_filter(thread)
                )
            elif mode == "rl":
                # during rl we are interested in all possible prefixes ending in prompter messages
                return thread[-1].role == "prompter" and not any(m.deleted or m.synthetic for m in thread)

            raise RuntimeError()

        visit_threads_depth_first(tree.prompt, visitor=threads.append, predicate=leaf_filter)
        if mode == "sft":
            for t in threads:
                if t[-1].role == "prompter":
                    t.pop()

        threads_per_tree.append(threads)

    def process_thread(thread):
        if mode == "sft":
            return [m.text for m in thread]
        elif mode == "rm":
            prefix = [m.text for m in thread]
            replies = [r for r in thread[-1].replies if r.role == "assistant" and r.rank is not None]
            replies = sorted(replies, key=lambda r: r.rank)
            replies = [r.text for r in replies]
            return (prefix, replies)
        elif mode == "rl":
            return ([m.text for m in thread],)

        raise RuntimeError()

    # split on tree basis, messages from same tree must not end up in different splits
    trees = ListDataset(threads_per_tree)
    splits = random_split(trees, lengths=[1.0 - val_split, val_split], generator=generator)

    def flatten(ds: ListDataset) -> ListDataset:
        return ListDataset([process_thread(thread) for tree_threads in ds for thread in tree_threads])

    train = flatten(splits[0])
    val = flatten(splits[1])

    print(f"OASST data {str(input_file_path)}: {len(train)=}, {len(val)=}")

    return train, val
