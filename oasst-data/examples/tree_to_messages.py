import argparse
import gzip
import json
from pathlib import Path

from oasst_data import ExportMessageNode, load_trees, visit_messages_depth_first


def parse_args():
    parser = argparse.ArgumentParser(description="tree_to_messages")
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
    parser.add_argument("--exclude-nulls", action="store_true", default=False)
    args = parser.parse_args()
    return args


def write_messages_file(
    output_file_name: str | Path,
    messages: list[ExportMessageNode],
    exclude_none: bool,
) -> None:
    output_file_name = Path(output_file_name)
    if output_file_name.suffix == ".gz":
        file = gzip.open(str(output_file_name), mode="wt", encoding="UTF-8")
    else:
        file = output_file_name.open("w", encoding="UTF-8")

    with file:
        # write one message per line
        for message in messages:
            message = message.copy(deep=False, exclude={"replies"})
            json.dump(message.dict(exclude_none=exclude_none), file)
            file.write("\n")


def main():
    """Read oasst message-trees from input file and generate a flat messages table output file."""
    args = parse_args()

    # read all messages of input file into a list
    messages: list[ExportMessageNode] = []
    print(f"reading: {args.input_file_name}")
    tree_count = 0
    for message_tree in load_trees(args.input_file_name):

        def append_with_tree_state(msg: ExportMessageNode):
            msg.tree_state = message_tree.tree_state
            msg.message_tree_id = message_tree.message_tree_id
            messages.append(msg)

        visit_messages_depth_first(message_tree.prompt, append_with_tree_state)
        tree_count += 1
    print(f"{tree_count} trees with {len(messages)} total messages read.")

    # write messages file
    print(f"writing: {args.output_file_name}")
    write_messages_file(args.output_file_name, messages, args.exclude_nulls)
    print(f"{len(messages)} messages written.")


if __name__ == "__main__":
    main()
