"""
    Recursive method to travese down the the conversation tree

    Use fastlangid for language identification :
    >> pip install fastlangid

"""
import glob
import json
import random
import sys
from collections import defaultdict
from copy import deepcopy

from fastlangid.langid import LID

langid = LID()
total_ranks = []
target_file = sys.argv[1]

attributes = [
    "message_id",
    "parent_id",
    "text",
    "role",
    "lang",
    "review_count",
    "rank",
    "synthetic",
    "model_name",
    "emojis",
]


def rank_replies(replies):
    return sorted(replies, key=lambda x: x["rank"])


def expand_nodes(tree):
    all_convo = []

    def traverse_tree(tree, root):
        if len(tree["replies"]) == 0:
            all_convo.append(root)
            return

        for reply in tree["replies"]:
            new_root = deepcopy(root)
            new_root.append({attr: reply[attr] for attr in attributes if attr in reply})
            traverse_tree(reply, new_root)

    init_root = [{attr: tree[attr] for attr in attributes if attr in tree}]
    traverse_tree(tree, init_root)
    return all_convo


def extract_all_pair_rank(tree):
    pairs = []

    def traverse_tree(tree, root):
        if len(tree["replies"]) == 0:
            return

        if tree["role"] == "prompter" and len(tree["replies"]) > 1:
            available_reply = [{attr: r[attr] for attr in attributes if attr in r} for r in tree["replies"]]
            pairs.append((root, available_reply))

        for reply in tree["replies"]:
            new_root = deepcopy(root)
            new_root.append({attr: reply[attr] for attr in attributes if attr in reply})
            traverse_tree(reply, new_root)

    init_root = [{attr: tree[attr] for attr in attributes if attr in tree}]
    traverse_tree(tree, init_root)
    return pairs


def viz_convo(conversation):
    for text in conversation:
        print(text["role"], ":", text["text"])


def calculate_total_threads(_target_file):
    total = 0
    lang_stats = defaultdict(int)
    with open(_target_file, "r") as f:
        print(_target_file)
        for line in f:
            row = json.loads(line)
            seed_prompt = row["prompt"]
            all_convo = expand_nodes(row["prompt"])
            for convo in all_convo:
                for convo_ in convo:
                    lang = langid.predict(convo_["text"])
                    lang_stats[lang] += 1

            if len(all_convo) > 1:
                total += len(all_convo)
            assert seed_prompt["role"] == "prompter"
    print(total)
    print(lang_stats)


def process_context(convo):
    if len(convo) == 1:
        return {"prompt": convo[0]["text"], "history": []}
    last_prompt = convo[-1]
    convo.pop(-1)
    history_pair = []
    for idx in range(0, len(convo), 2):
        history_pair.append((convo[idx]["text"], convo[idx + 1]["text"]))

    return {"prompt": last_prompt["text"], "history": history_pair}


if __name__ == "__main__":
    calculate_total_threads(target_file)

    usable_rank = 0
    response_with_rank = 0
    RM_dataset = []
    with open(target_file, "r") as f:
        for line in f:
            row = json.loads(line)
            seed_prompt = row["prompt"]
            initial = seed_prompt["text"]
            all_convo = extract_all_pair_rank(row["prompt"])
            for convo, replies in all_convo:
                if len(replies) > 1:
                    prefix = process_context(convo)
                    if "rank" not in replies[0]:
                        continue
                    elif replies[0]["rank"] is not None:
                        for r in replies:
                            if "rank" in r and r["rank"] is None:
                                r["rank"] = 5
                            elif "rank" not in r:
                                r["rank"] = 5
                        replies = sorted(replies, key=lambda x: x["rank"])
                        pos_reply = replies[0]["text"]
                        neg_replies = [r["text"] for r in replies[1:]]

                        RM_dataset.append(
                            {
                                "prompt": prefix["prompt"],
                                "history": prefix["history"],
                                "pos": pos_reply,
                                "neg_replies": neg_replies,
                            }
                        )

                        response_with_rank += 1

            usable_rank += len(all_convo)

    print(len(RM_dataset), usable_rank)

    key_sets = set()
    for rm_jsonl in glob.glob("rm_*.jsonl"):
        with open(rm_jsonl, "r") as f:
            for line in f:
                data = json.loads(line)
                key = "{}-{}-{}".format(data["prompt"], data["pos"], "".join(data["neg_replies"]))
                key_sets.add(key)

    new_dataset = []
    for data in RM_dataset:
        key = "{}-{}-{}".format(data["prompt"], data["pos"], "".join(data["neg_replies"]))
        if key not in key_sets:
            new_dataset.append(data)

    with open("rm_new.jsonl", "w") as f:
        for row in new_dataset:
            f.write(json.dumps(row) + "\n")

    random.shuffle(RM_dataset)
    train_flag = int(len(RM_dataset) * 0.8)
    test_flag = int(len(RM_dataset) * 0.9)
    train, test, val = RM_dataset[:train_flag], RM_dataset[train_flag:test_flag], RM_dataset[test_flag:]
    with open("rm_train.jsonl", "w") as f:
        for row in train:
            f.write(json.dumps(row) + "\n")
    with open("rm_test.jsonl", "w") as f:
        for row in test:
            f.write(json.dumps(row) + "\n")
    with open("rm_val.jsonl", "w") as f:
        for row in val:
            f.write(json.dumps(row) + "\n")
