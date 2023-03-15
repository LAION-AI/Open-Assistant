import argparse

from oasst_data import ExportMessageTree, load_tree_list, visit_messages_depth_first


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path", type=str, help=".jsonl or jsonl.gz OA export")
    parser.add_argument("--lang", type=str, help="comma separated list of lang-codes")
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

    def tree_filter(tree: ExportMessageTree) -> bool:
        return (
            tree.tree_state == "ready_for_export"
            and tree.prompt.review_result
            and (lang_codes is None or tree.prompt.lang in lang_codes)
        )

    trees = load_tree_list(args.input_file_path, filter=tree_filter)
    print(f"{len(trees)} trees")

    all_messages = []
    for t in trees:
        visit_messages_depth_first(t.prompt, all_messages.append)
    synthetic_messages = [m for m in all_messages if m.synthetic]
    prompter_messages = [m for m in all_messages if m.role == "prompter"]
    assistant_messages = [m for m in all_messages if m.role == "assistant"]

    print(f"{len(all_messages)} messages")
    print(f"{len(synthetic_messages)} synthetic messages")
    print(f"{len(prompter_messages)} prompter messages")
    print(f"{len(assistant_messages)} assistant messages")

    prompter_with_replies = [m for m in prompter_messages if m.replies and len(m.replies) > 1]
    print(f"{len(prompter_with_replies)} prompter messages with >1 reply")

    prompter_with_replies_ranked = [
        m
        for m in prompter_messages
        if m.replies and len([rm for rm in m.replies if rm.rank is not None and rm.rank >= 0]) > 1
    ]
    print(f"{len(prompter_with_replies_ranked)} prompter messages with >1 ranked reply")


if __name__ == "__main__":
    main()
