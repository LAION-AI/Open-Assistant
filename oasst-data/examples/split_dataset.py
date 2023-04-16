import argparse
import random

from oasst_data import read_message_list, write_messages


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--val_percent",
        type=int,
        default=5,
    )
    parser.add_argument(
        "input_file_name",
        type=str,
        help="path to input .jsonl or .jsonl.gz input file",
    )
    parser.add_argument(
        "--val_output",
        type=str,
        help="path to validation output .jsonl or .jsonl.gz file",
        required=True,
    )
    parser.add_argument(
        "--train_output",
        type=str,
        help="path to train output .jsonl or .jsonl.gz file",
        required=True,
    )
    parser.add_argument("--exclude-nulls", action="store_true", default=False)
    args = parser.parse_args()
    return args


def main():
    """Split messages file into train and validation set based on message_tree_id."""
    args = parse_args()

    print(f"Reading: {args.input_file_name}")
    messages = read_message_list(args.input_file_name)

    print(f"Found {len(messages)} matching messages.")

    tree_ids = list(set(m.message_tree_id for m in messages))
    random.shuffle(tree_ids)

    val_size = len(tree_ids) * args.val_percent // 100

    train_set = set(tree_ids[val_size:])
    val_set = set(tree_ids[:val_size])

    train_messages = [m for m in messages if m.message_tree_id in train_set]
    val_messages = [m for m in messages if m.message_tree_id in val_set]

    print(f"Writing train {len(train_messages)} messages: {args.train_output}")
    write_messages(args.train_output, train_messages, args.exclude_nulls)

    print(f"Writing valid {len(val_messages)} messages: {args.val_output}")
    write_messages(args.val_output, val_messages, args.exclude_nulls)


if __name__ == "__main__":
    main()
