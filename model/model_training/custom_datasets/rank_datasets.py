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

    def __init__(self, split):
        super().__init__()

        self.post_dict = defaultdict(dict)
        self.postids = []
        if not isinstance(split, List):
            split = [split]
        dataset = load_dataset("stanfordnlp/SHP", split=split)
        for data in dataset:
            for item in data:
                postid = item.get("post_id")
                self.postids.append(postid)
                score_A, score_B = [item.get(key) for key in ("score_A", "score_B")]
                answers = [item.get(key) for key in ("human_ref_A", "human_ref_B")]
                if score_B > score_A:
                    answers = list(reversed(answers))

                self.post_dict[postid].update({"post": item.get("history"), "answers": answers})

    def __len__(self):
        return len(self.postids)

    def __getitem__(self, idx):
        postid = self.postids[idx]
        post, answers = self.post_dict.get(postid, {}).values()
        return [post], answers


class HellaSwagDataset(Dataset):
    """
    Dataset class to use data from https://arxiv.org/pdf/1905.07830.pdf
    for Reward modeling
    """

    name = "hellaswag"

    def __init__(self, split) -> None:
        super().__init__()

        np.random.seed(SEED)
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

    name = "hfsummary"

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
