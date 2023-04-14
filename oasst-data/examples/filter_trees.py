import argparse
import gzip
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from oasst_data import load_trees, visit_messages_depth_first
from oasst_data.schemas import ExportMessageTree


def write_message_trees(
    output_file_name: str | Path,
    trees: Iterable[ExportMessageTree],
    exclude_none: bool,
) -> None:
    output_file_name = Path(output_file_name)
    if output_file_name.suffix == ".gz":
        file = gzip.open(str(output_file_name), mode="wt", encoding="UTF-8")
    else:
        file = output_file_name.open("w", encoding="UTF-8")

    def default_serializer(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    with file:
        # write one tree per line
        for tree in trees:
            json.dump(
                tree.dict(exclude_none=exclude_none), file, default=default_serializer
            )
            file.write("\n")


def parse_args():
    parser = argparse.ArgumentParser(description="filter_tres")
    parser.add_argument(
        "input_file_name",
        type=str,
        help="path to input .jsonl or .jsonl.gz input file",
    )
    parser.add_argument(
        "output_file_name",
        type=str,
        help="path to output .jsonl or .jsonl.gz file",
    )
    parser.add_argument(
        "--states",
        type=str,
        default="ready_for_export",
        help="all|prompt_lottery_waiting|growing|ready_for_export|aborted_low_grade|halted_by_moderator|backlog_ranking",
    )
    parser.add_argument("--exclude-nulls", action="store_true", default=False)
    parser.add_argument("--allow-synth", action="store_true", default=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    # load dataset and index messages by id
    trees: list[ExportMessageTree] = []

    states = args.states.split(",")
    allow_synth = args.allow_synth

    print(f"Reading: {args.input_file_name}")
    for message_tree in load_trees(args.input_file_name):
        msgs = []
        visit_messages_depth_first(message_tree.prompt, msgs.append)
        if message_tree.tree_state in states and (
            allow_synth or not any(x.synthetic for x in msgs)
        ):
            trees.append(message_tree)

    print(f"Found {len(trees)} matching trees.")

    print(f"Writing: {args.output_file_name}")
    write_message_trees(args.output_file_name, trees, exclude_none=args.exclude_nulls)


if __name__ == "__main__":
    main()
