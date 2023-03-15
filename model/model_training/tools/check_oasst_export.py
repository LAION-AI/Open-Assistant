import argparse
import gzip
import json
from pathlib import Path
from typing import Callable, Optional

import pydantic
from oasst_data import ExportMessageNode, ExportMessageTree


def load_trees(input_file_path: str | Path, lang_codes: Optional[list[str]] = None) -> list[ExportMessageTree]:
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)
    if input_file_path.suffix == ".gz":
        file_in = gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
    else:
        file_in = input_file_path.open("r", encoding="UTF-8")

    trees = []
    with file_in:
        # read one message tree per line
        for line in file_in:
            dict_tree = json.loads(line)

            # validate data
            tree: ExportMessageTree = pydantic.parse_obj_as(ExportMessageTree, dict_tree)

            if (
                tree.tree_state != "ready_for_export"
                or not tree.prompt.review_result
                or (lang_codes is not None and tree.prompt.lang not in lang_codes)
            ):
                continue

            trees.append(tree)

    return trees


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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path", type=str)
    parser.add_argument("--lang", type=str)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    lang_codes = None
    if args.lang:
        lang_codes = args.lang.split(",")

    print(f"input file: {args.input_file_path}")

    if lang_codes is None:
        print("Using languages: all")
    else:
        print(f'Filtering languages: {", ".join(lang_codes)}')

    trees = load_trees(args.input_file_path, lang_codes=lang_codes)
    print(f"{len(trees)} tree")

    all_messages = []
    for t in trees:
        _visit_threads_depth_first(t.prompt, lambda t: all_messages.append(t[-1]))
    prompter_messages = [m for m in all_messages if m.role == "prompter"]
    assistant_messages = [m for m in all_messages if m.role == "assistant"]
    print(f"{len(all_messages)} messages")
    print(f"{len(prompter_messages)} prompter messages")
    print(f"{len(assistant_messages)} assistant messages")

    prompter_with_replies = [m for m in prompter_messages if m.replies and len(m.replies) > 1]

    print(f"{len(prompter_with_replies)} prompter messages with >1 reply")


if __name__ == "__main__":
    main()
