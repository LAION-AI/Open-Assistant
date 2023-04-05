import random
from collections import defaultdict
from typing import List

import numpy as np
from datasets import load_dataset
from torch.utils.data import Dataset

SEED = 2020


class SHPDataset(Dataset):
    """
    Dataset class to load stanfordnlp/SHP for Reward Modeling
    """

    name = "SHP"

    def __init__(self, split, max_answers: int = 5):
        super().__init__()
        self.max_answers = max_answers
        self.questions = []
        self.answers = []

        if not isinstance(split, list):
            split = [split]
        dataset_splits = load_dataset("stanfordnlp/SHP", split=split)
        for split in dataset_splits:
            question_answer_dict = defaultdict(dict)
            for row in split:
                history = row["history"]
                question_answer_dict[history][row["human_ref_A"]] = row["score_A"]
                question_answer_dict[history][row["human_ref_B"]] = row["score_B"]

            for question, answers in question_answer_dict.items():
                self.questions.append(question)
                # Sort answer dict with the highest score first (hence the prefactor -1).
                # Then take only the first `max_answers` elements (usually there are just
                # 2, but there are examples where we have more)
                a = [x[0] for x in sorted(answers.items(), key=lambda x: -1 * x[1])]
                self.answers.append(a[: self.max_answers])

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, index):
        return [self.questions[index]], self.answers[index]


class HellaSwagDataset(Dataset):
    """
    Dataset class to use data from https://arxiv.org/pdf/1905.07830.pdf
    for Reward modeling
    """

    name = "hellaswag"

    def __init__(self, split, seed=SEED) -> None:
        super().__init__()

        np.random.seed(seed)
        self.dataset_list = []
        if not isinstance(split, List):
            split = [split]
        dataset = load_dataset("AlekseyKorshuk/hellaswag", split=split)
        for data in dataset:
            for item in data:
                context = item.get("ctx")
                endings = item.get("endings")
                selected = endings.pop(item.get("label"))
                ordered_ends = [selected, np.random.choice(endings)]
                self.dataset_list.append({"context": context, "completions": ordered_ends})

    def __len__(self):
        return len(self.dataset_list)

    def __getitem__(self, idx):
        context, completions = self.dataset_list[idx].values()
        return [context], completions


class HFDataset(Dataset):
    """
    Dataset class to use data from openai/summarize_from_feedback for Reward modeling.
    Summaries ranked by overall score.
    """

    name = "open_ai_summarize_from_feedback"

    def __init__(self, split=None, subset="axis") -> None:
        super().__init__()
        # axis subset contains splits 'test' and 'validation'
        # comparisons subset contains splits 'train' and 'validation'
        if not isinstance(split, List):
            split = [split]
        dataset = load_dataset("openai/summarize_from_feedback", subset, split=split)
        self.subset = subset

        # in axis subset the summaries are ranked
        self.axis_post_ids = []
        self.axis_post_dict = defaultdict(dict)

        # in comparison subset we have each time a pair
        # of summarizations and then the chosen out of 2
        self.comparisons = []

        if subset == "axis":
            self._handle_axis(dataset)
        else:
            self._handle_comparisons(dataset)

    def _handle_comparisons(self, dataset):
        for data in dataset:
            for item in dataset:
                choice = item["choice"]  # indicates the preferred summary
                full_post = item["info"]["post"]
                summaries = [item["summaries"][choice]["text"], item["summaries"][1 - choice]["text"]]
                self.comparisons.append([[full_post], summaries])

    def _handle_axis(self, dataset):
        for data in dataset:
            for item in dataset:
                if item["summary"].get("axes").get("overall") is not None:
                    post_id = item.get("info")["id"]
                    if post_id not in self.axis_post_ids:
                        self.axis_post_ids.append(post_id)
                        item_content = item["info"]["post"] or item["info"]["article"]
                        self.axis_post_dict[post_id].update({"post": item_content, "summaries": [item["summary"]]})
                    else:
                        self.axis_post_dict[post_id]["summaries"].append(item["summary"])

    def __len__(self):
        if self.subset == "axis":
            return len(self.axis_post_ids)
        return len(self.comparisons)

    def __getitem__(self, idx):
        post, summaries = self.post_dict[self.post_ids[idx]].values()
        summaries = sorted(summaries, key=lambda x: x["axes"]["overall"], reverse=True)
        summaries = [summary["text"] for summary in summaries]
        return [post], summaries


class AugmentedOA(Dataset):
    def __init__(self, json_filename, split="train") -> None:
        super().__init__()
        import json

        assert split in ("train", "val")

        pairs = []
        with open(json_filename, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                if data["split"] == split:
                    augmented = data["augmented"]
                    if split == "val":  # disable augmentation during validation
                        augmented = []
                    pairs.append((data["prefixes"], data["responses"], augmented))
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        prefixes, user_answer_ranks, bad_samples = self.pairs[idx]
        # we want to prevent modifying user_answer_ranks
        rank = user_answer_ranks
        if len(bad_samples) > 0:
            additional = random.choice(bad_samples)
            rank = user_answer_ranks + [additional]

        return prefixes, rank
        if self.subset == "axis":
            post, summaries = self.axis_post_dict[self.axis_post_ids[idx]].values()
            summaries = sorted(summaries, key=lambda x: x["axes"]["overall"], reverse=True)
            summaries = [summary["text"] for summary in summaries]
            return [post], summaries
        return self.comparisons[idx]


class AnthropicRLHF(Dataset):
    name = "anthropic_rlhf"

    @staticmethod
    def _split_dialogue(text):
        lines = text.split("\n\n")

        dialogue = []
        for line in lines:
            if line.startswith("Human:"):
                speaker = "Human"
                message = line[7:]
            elif line.startswith("Assistant:"):
                speaker = "Assistant"
                message = line[11:]
            else:
                continue
            dialogue.append((speaker, message.strip()))

        return dialogue

    def __init__(self, split="train") -> None:
        super().__init__()
        assert split in ("train", "test")
        self.split = split
        self.data = []
        dataset = load_dataset("Anthropic/hh-rlhf")[split]
        for entry in dataset:
            chosen = entry["chosen"]

            if "Assistant" not in chosen:
                continue

            rejected = entry["rejected"]
            chosen = self._split_dialogue(chosen)
            rejected = self._split_dialogue(rejected)

            prefix = [line for (speaker, line) in chosen[:-1]]
            good_reply = chosen[-1][1]  # last part of dialog, the text
            bad_reply = rejected[-1][1]  # last part of dialog, the text
            self.data.append((prefix, [good_reply, bad_reply]))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


class WebGPTRank(Dataset):
    name = "webgpt"  # use mode="rm" when calling get_one_dataset()

    def __init__(self, max_answers: int = 5) -> None:
        super().__init__()
        self.max_answers = max_answers

        dataset = load_dataset("openai/webgpt_comparisons")
        self.questions = []
        self.answers = []
        question_answer_dict = defaultdict(dict)
        for row in dataset["train"]:
            question = row["question"]["full_text"]
            question_answer_dict[question][row["answer_0"]] = row["score_0"]
            question_answer_dict[question][row["answer_1"]] = row["score_1"]
        for question, answers in question_answer_dict.items():
            self.questions.append(question)
            # Sort answer dict with the highest score first (hence the prefactor -1).
            # Then take only the first `max_answers` elements (usually there are just
            # 2, but there are examples where we have more)
            a = [x[0] for x in sorted(answers.items(), key=lambda x: -1 * x[1])]
            self.answers.append(a[: self.max_answers])

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, index):
        return [self.questions[index]], self.answers[index]
