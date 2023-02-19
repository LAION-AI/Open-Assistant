import json
from collections import defaultdict
from typing import List

import pandas as pd


def load_jsonl(filepaths):
    data = []
    for filepath in filepaths:
        with open(filepath, "r") as f:
            for line in f:
                data.append(json.loads(line))
    return data


def separate_qa_helper(node, depth, msg_dict):
    if "text" in node:
        if node["role"] == "prompter":
            msg_dict["user_messages"].append(str(node["text"]))
        elif node["role"] == "assistant":
            msg_dict["assistant_messages"].append(str(node["text"]))
        depth += 1
        if "replies" in node:
            for reply in node["replies"]:
                separate_qa_helper(reply, depth, msg_dict)


def store_qa_data_separate(trees, data):
    message_list = []
    for i, msg_tree in enumerate(trees):
        if "prompt" in msg_tree.keys():
            separate_qa_helper(msg_tree["prompt"], i, data)
        elif "prompt" not in msg_tree.keys():
            message_list.append(msg_tree)
    return data, message_list


def group_qa_helper(node, depth, msg_pairs):
    if "text" in node:
        if node["role"] == "prompter":
            if "replies" in node:
                for reply in node["replies"]:
                    qa_pair = {"instruct": str(node["text"]), "answer": str(reply["text"])}
                    msg_pairs.append(qa_pair)
        depth += 1
        if "replies" in node:
            for reply in node["replies"]:
                group_qa_helper(reply, depth, msg_pairs)


def store_qa_data_paired(trees, data: List):
    message_list = []
    for i, msg_tree in enumerate(trees):
        if "prompt" in msg_tree.keys():
            group_qa_helper(msg_tree["prompt"], i, data)
        elif "prompt" not in msg_tree.keys():
            message_list.append(msg_tree)
    return data, message_list


def load_data(filepaths: List[str], paired=False):
    trees = load_jsonl(filepaths)
    if paired:
        data = []
        data, message_list = store_qa_data_paired(trees, data)
        sents = [f"{qa['instruct']} {qa['answer']}" for qa in data]
    elif not paired:
        data = defaultdict(list)
        data, message_list = store_qa_data_separate(trees, data)
        sents = data["user_messages"] + data["assistant_messages"]

    data = [(i, sent) for i, sent in enumerate(sents)]
    data = pd.DataFrame(data, columns=["id", "query"])
    return data, message_list
