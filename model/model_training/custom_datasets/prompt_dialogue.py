import json
import math
import os
import random
from collections import OrderedDict
from functools import reduce
from urllib.request import urlopen

import numpy as np
from custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pair
from torch.utils.data import Dataset


class OAPrivate(Dataset):
    splits = OrderedDict(sft=0.25, reward_model=0.4, rl=0.35)  # fractions per task

    def __init__(self, data_path, split="sft", file="2023-02-10_oasst_prod.jsonl") -> None:
        super().__init__()

        total_prob = reduce(lambda prev, split: prev + split[1], self.splits.items(), 0)
        assert math.isclose(total_prob, 1), "Make sure OAPrivate split ratios add to 1"

        self.mode = split

        jsonl_file = os.path.join(data_path, file)

        with open(jsonl_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # take a subset of the dataset based on the split
        rng = np.random.default_rng(seed=0)
        indices = np.arange(len(lines)).astype(int)
        rng.shuffle(indices)

        cumsums = np.cumsum([[0] + list(self.splits.values())])
        split_index = list(self.splits.keys()).index(split)

        start_index, end_index = int(cumsums[split_index] * len(lines)), int(cumsums[split_index + 1] * len(lines))

        self.data = [json.loads(lines[index].strip()) for index in indices[start_index:end_index]]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        # Sample randomly from replies
        prompt = self.data[index]["prompt"]

        pairs = []

        while True:
            assert prompt["role"] == "prompter"
            prompter_text = prompt["text"]

            if len(prompt["replies"]) == 0:
                break

            reply = random.choice(prompt["replies"])
            reply_text = reply["text"]

            # only add if the reply exists
            pairs.append(prompter_text)
            pairs.append(reply_text)

            if len(reply["replies"]) == 0:
                break

            prompt = random.choice(reply["replies"])

        if self.mode == "sft":
            # return all dialogue history
            return format_pair(pairs)
        elif self.mode == "rl":
            # random stop at the end of a new prompt
            pairs = format_pair(pairs[: random.choice([i for i in range(len(pairs)) if i % 2 == 1])])
            return "".join(pairs)


class PromptGeneratedDataset(Dataset):
    """Generates from flan 11B
    User: What are the best methods for preventing a slave trade?

    Rosey: The best methods ....
    <|endoftext|>

    we are ignoring results with multiple lines for now
    """

    name = "prompt_dialogue"
    url = "https://github.com/Rallio67/language-model-agents/raw/main/chat_dialogue_v2_c.txt"

    def __init__(self, cache_dir) -> None:
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)
        chat_dialogue = os.path.join(cache_dir, "chat_dialogue_v2_c.txt")
        if not os.path.exists(chat_dialogue):
            with urlopen(self.url) as file:
                content = file.read().decode()
            with open(chat_dialogue, "w") as fout:
                fout.write(content)

        question = ""
        answer = ""
        self.pairs = []
        with open(chat_dialogue, "r") as f:
            corpus = f.read().split("<|endoftext|>")
            for dialogue in corpus:
                dialogue = dialogue.strip()
                if "Rosey:" in dialogue:
                    user, bot = dialogue.split("Rosey:", maxsplit=1)
                    question = user.split(":", maxsplit=1)[1].strip()
                    answer = bot.strip()
                    if len(answer) and len(question):
                        self.pairs.append((question, answer))

        if len(question) > 0 and len(answer) > 0:
            self.pairs.append((question, answer))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        return format_pair(self.pairs[index])


class InstructionTuning(Dataset):
    """
    We have seen some promising capabilities from instruction tuning
    with the following mix of datasets that are derived from datasets
    available online.
    The files for this data are in json format as a list of tuples
    where each tuple is (source,instruction_response_pair)

        - instruction_tuning_dataset_alpha_part1.json
        - instruction_tuning_dataset_alpha_part2.json

    Not to be confused with unatural instruction
    """

    name = "instruction_dataset"
    url_part_2 = (
        "https://github.com/Rallio67/language-model-agents/raw/main/instruction_tuning_dataset_alpha_part2.json"
    )
    url_part_1 = (
        "https://github.com/Rallio67/language-model-agents/raw/main/instruction_tuning_dataset_alpha_part1.json"
    )

    def __init__(self, cache_dir) -> None:
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)

        self.pairs = []
        for file_link in [self.url_part_1, self.url_part_2]:
            basename = file_link.split("/")[-1]
            instruction_tune_file = os.path.join(cache_dir, basename)
            if not os.path.exists(instruction_tune_file):
                with urlopen(file_link) as file:
                    content = file.read().decode()
                with open(instruction_tune_file, "w", encoding="utf-8") as fout:
                    fout.write(content)

            with open(instruction_tune_file, "r", encoding="utf-8") as f:
                datasets = json.load(f)
                for row in datasets:
                    _, response_pair = row
                    question, answer = response_pair.split("\n\n", maxsplit=1)
                    answer = answer.replace("<|endoftext|>", "").strip()
                    self.pairs.append((question, answer))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        return format_pair(self.pairs[index])


class PrivateInstructionTuning(Dataset):
    """
    We have seen some promising capabilities from instruction tuning
    with the following mix of datasets that are derived from datasets
    available online.
    The files for this data are in json format as a list of tuples
    where each tuple is (source,instruction_response_pair)

    Not to be confused with unatural instruction
    """

    name = "private_tuning"
    filename = "oa_v3_fixed_plus_safety.jsonl"

    def __init__(self, cache_dir) -> None:
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)

        self.pairs = []
        for file_link in [self.filename]:
            basename = file_link.split("/")[-1]
            instruction_tune_file = os.path.join(cache_dir, basename)

            with open(instruction_tune_file, "r", encoding="utf-8") as f:
                for line in f:
                    row = json.loads(line)
                    prefix = ""
                    for _, convo in enumerate(row["text"].split("User:")):
                        if "Assistant" in convo:
                            prompt, answer = convo.split("Assistant:", maxsplit=1)
                            answer = answer.replace("<|endoftext|>", "").strip()
                            self.pairs.append((prefix + QA_SPECIAL_TOKENS["Question"] + prompt, answer))
                            prefix += "".join(format_pair((prompt, answer)))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        prompt, answer = self.pairs[index]
        return "{}{}".format(prompt, QA_SPECIAL_TOKENS["Answer"]), answer
