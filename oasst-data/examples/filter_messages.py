import argparse
import json

from oasst_data import read_message_list, write_messages
from oasst_data.schemas import ExportMessageNode
from oasst_data.writer import open_jsonl_write


def parse_args():
    parser = argparse.ArgumentParser(description="filter_messages")
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
        "--include-deleted",
        action="store_true",
        help="Include deleted messages in export",
    )
    parser.add_argument(
        "--deleted-only",
        action="store_true",
        help="Export only deleted messages (implies --include-deleted)",
    )
    parser.add_argument(
        "--include-spam",
        action="store_true",
        help="Export including messages with no review or negative review result.",
    )
    parser.add_argument(
        "--spam-only",
        action="store_true",
        help="Export only messages with negative review result (implies --include-spam).",
    )
    parser.add_argument(
        "--exclude-normal",
        action="store_true",
        help="exclude non-deleted non-synthetic messages with positive review",
        default=False,
    )
    parser.add_argument(
        "--include-synthetic",
        action="store_true",
        help="Include synthetic messages in export",
    )
    parser.add_argument(
        "--synthetic-only",
        action="store_true",
        help="Export only synthetic messages (implies --include-synth)",
    )
    parser.add_argument(
        "--user",
        type=str,
        help="Only export trees involving the user with the specified ID. Incompatible with --state.",
    )
    parser.add_argument(
        "--state",
        type=str,
        help="all|prompt_lottery_waiting|growing|ready_for_export|aborted_low_grade|halted_by_moderator|backlog_ranking",
    )
    parser.add_argument(
        "--lang",
        type=str,
        help="Filter message trees by language code (BCP 47)",
    )
    parser.add_argument(
        "--prompts-only",
        action="store_true",
        help="Export a list of initial prompt messages",
    )
    parser.add_argument(
        "--export-text-only",
        action="store_true",
        help="Write jsonl file with message text strings only",
    )
    parser.add_argument("--exclude-nulls", action="store_true", default=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    deleted: bool | None = False
    spam: bool | None = False
    synthetic: bool | None = False
    langs: list[str] | None = None
    states: list[str] | None = None
    prompts_only: bool = args.prompts_only
    exclude_normal: bool = args.exclude_normal

    if args.include_deleted:
        deleted = None
    elif args.deleted_only:
        deleted = True

    if args.include_spam:
        spam = None
    elif args.spam_only:
        spam = True

    if args.include_synthetic:
        synthetic = None
    elif args.synthetic_only:
        synthetic = True

    if args.lang:
        langs = args.lang.split(",")

    if args.state:
        states = args.state.split(",")

    def approve_message(msg: ExportMessageNode) -> bool:
        if (
            (deleted is not None and msg.deleted != deleted)
            or (synthetic is not None and msg.synthetic != synthetic)
            or (prompts_only and msg.parent_id)
            or (langs is not None and msg.lang not in langs)
            or (states is not None and msg.tree_state not in states)
        ):
            return False

        if exclude_normal is True and not msg.deleted and not msg.synthetic and msg.review_result:
            return False

        if spam is not None and spam != (not msg.review_result):
            return False

        return True

    print(f"Reading: {args.input_file_name}")
    messages = read_message_list(args.input_file_name, approve_message)

    print(f"Found {len(messages)} matching messages.")

    print(f"Writing: {args.output_file_name}")
    if args.export_text_only:
        with open_jsonl_write(args.output_file_name) as file:
            for msg in messages:
                json.dump(msg.text, file)
                file.write("\n")
    else:
        write_messages(args.output_file_name, messages, args.exclude_nulls)


if __name__ == "__main__":
    main()
