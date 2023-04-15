import argparse

from oasst_data import read_message_trees, write_message_trees
from oasst_data.schemas import ExportMessageTree
from oasst_data.traversal import visit_messages_depth_first


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
    for message_tree in read_message_trees(args.input_file_name):
        msgs = []
        visit_messages_depth_first(message_tree.prompt, msgs.append)
        if message_tree.tree_state in states:
            if allow_synth or not any(x.synthetic for x in msgs):
                trees.append(message_tree)

    print(f"Found {len(trees)} matching trees.")

    print(f"Writing: {args.output_file_name}")
    write_message_trees(args.output_file_name, trees, exclude_none=args.exclude_nulls)


if __name__ == "__main__":
    main()
