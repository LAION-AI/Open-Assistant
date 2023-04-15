import argparse
from collections import OrderedDict

import pandas
from oasst_data.reader import read_message_trees
from oasst_data.schemas import ExportMessageNode, ExportMessageTree
from oasst_data.traversal import visit_messages_depth_first
from oasst_data.writer import write_message_trees


def parse_args():
    parser = argparse.ArgumentParser(description="filter_dataset")
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
    parser.add_argument("--instructions", type=str, help="xlsx file with instructions")
    parser.add_argument("--exclude-nulls", action="store_true", default=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    instructions_df = pandas.read_excel(args.instructions, na_filter=False)

    # load dataset and index messages by id
    tree_by_id: dict[str, ExportMessageTree] = OrderedDict()
    message_by_id: dict[str, ExportMessageNode] = {}

    print(f"Reading: {args.input_file_name}")
    for message_tree in read_message_trees(args.input_file_name):
        tree_by_id[message_tree.message_tree_id] = message_tree

        def index_message(msg: ExportMessageNode):
            message_by_id[msg.message_id] = msg

        visit_messages_depth_first(message_tree.prompt, index_message)

    print(f"Loaded {len(tree_by_id)} trees with {len(message_by_id)} messages.")

    def count_descendants(msg: ExportMessageNode):
        i = 1
        if msg.replies:
            for r in msg.replies:
                i += count_descendants(r)
        return i

    def delete_message(msg: ExportMessageNode):
        if msg.parent_id is None:
            tree_by_id.pop(msg.message_id)
            print(f"Tree deleted: {msg.message_id}")
        else:
            parent_msg = message_by_id[msg.parent_id]
            parent_msg.replies.remove(msg)
            print(f"Branch deleted: {msg.message_id} ({count_descendants(msg)} messages)")

    # cleaning
    print("Cleaning...")
    for index, row in instructions_df.iterrows():
        id = row["UUID"]
        msg = message_by_id.get(id)
        if msg is None:
            print(f"Not found: {id}")

        action = row["Action"]
        if action == "Delete":
            print(f"deleting: {id}")
            delete_message(msg)
        elif action == "Replace":
            print(f"replace: {id}")
            replace = row["Replace"]
            msg.text = replace
        elif action == "Edit":
            print(f"edit: {id}")
            if row["Category"] == "Copy Code":
                find = "\nCopy code\n"
                replace = "\n\n"
            else:
                find = row["Find"]
                replace = row["Replace"]
            msg.text.index(find)  # make sure text is present
            msg.text = msg.text.replace(find, replace)
        else:
            print(f"Unsupported action {action}")

    print("Done")

    # write cleaned dataset to output file
    print(f"Writing: {args.output_file_name}")
    write_message_trees(
        args.output_file_name,
        tree_by_id.values(),
        exclude_none=args.exclude_nulls,
    )


if __name__ == "__main__":
    main()
