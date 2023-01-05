# -*- coding: utf-8 -*-
"""
    author: theblackcat102

    Dataset output format from __getitem__

     - question / prompt : string

     - answers / rows : list of tuple pair. The first element in the tuple pair must be the positive pair (rank higher than the second element)

    A list of rank based dataset for training using rank loss

    Some nice features to have

    [] support additional negative samples generated from other models.

        For example we can use galactica-125m to generate a TLDR and assume it was
        inferior than the human perference one


"""
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
from datasets import load_dataset
from torch.utils.data import Dataset
from transformers.tokenization_utils_base import PaddingStrategy, PreTrainedTokenizerBase


@dataclass
class DataCollatorForPairRank:
    """

    Data collator that will dynamically pad the inputs for multiple choice received.

    """

    tokenizer: PreTrainedTokenizerBase
    num_choices: int = 2
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    drop_token_type: bool = False  # galactica

    def __call__(self, features):

        flatten_features = []
        batch_size = 0
        for question, pairs in features:
            for (pos, neg) in pairs:
                flatten_features.append(
                    self.tokenizer(
                        question, 
                        pos, 
                        truncation=True, 
                        max_length=self.max_length)
                    )
                flatten_features.append(
                    self.tokenizer(
                        question, 
                        neg, 
                        truncation=True, 
                        max_length=self.max_length)
                    )
                batch_size += 1

        batch = self.tokenizer.pad(
            flatten_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        if self.drop_token_type:
            batch.pop("token_type_ids")
        # batch = {k: v.view(batch_size, self.num_choices, -1) for k, v in batch.items()}
        return batch


class WebGPT(Dataset):
    def __init__(self) -> None:
        super().__init__()

        dataset = load_dataset("openai/webgpt_comparisons")
        questions = {}
        # using prompt as our index will allows us
        # to add additional generated prompt later
        self.index2question = {}
        for row in dataset["train"]:
            question = row["question"]["full_text"]
            if question not in self.index2question:
                self.index2question[len(self.index2question)] = question

            if question not in questions:
                questions[question] = []

            if row["score_0"] > row["score_1"]:
                # not going to risk it
                questions[question].append((row["answer_0"], row["answer_1"]))
            else:
                questions[question].append((row["answer_1"], row["answer_0"]))

        self.questions = questions

    def __len__(self):
        return len(self.index2question)

    def __getitem__(self, index):
        question = self.index2question[index]
        rows = self.questions[question]
        # optimize the format later
        return question, rows


class HFSummary(Dataset):
    """
    Human feedback data from OpenAI
    https://github.com/openai/summarize-from-feedback

    labeling method : pair comparison, 0 or 1

    """

    def __init__(self, split="train", conf_threshold=-1, max_comparison_per_sample=3) -> None:
        super().__init__()
        assert split in ("train", "valid1", "valid2", "test")
        summaries = {}
        # using prompt as our index will allows us
        # to add additional generated prompt later
        self.index2summary = {}
        self.max_comparison_per_sample = max_comparison_per_sample
        major_split = split if "train" == split else "validation"
        dataset = load_dataset("Tristan/summarize_from_feedback", "comparisons")[major_split]
        for data in dataset:
            if (
                "extra" in data
                and "confidence" in data["extra"]
                and data["extra"]["confidence"] is not None
                and conf_threshold > data["extra"]["confidence"]
            ):
                print("skipping {}".format(data["info"]["id"]))
                continue

            if split != "train" and split != data["split"]:
                continue

            if "article" in data["info"] and data["info"]["article"] is not None:
                context = data["info"]["article"]
            elif "post" in data["info"]:
                context = data["info"]["post"]

            if context not in self.index2summary:
                self.index2summary[len(self.index2summary)] = context

            if context not in summaries:
                summaries[context] = []

            pos, neg = (0, 1) if data["choice"] == 0 else (1, 0)
            summaries[context].append((data["summaries"][pos]["text"], data["summaries"][neg]["text"]))

        self.summaries = summaries

        self.postfix_prompt = " TLDR;"

    def __len__(self):
        return len(self.index2summary)

    def __getitem__(self, index):
        context = self.index2summary[index]
        # return pairs of comparison
        rows = self.summaries[context]
        # pair very big
        # we are going to do some sampling
        # not optimal but good for now
        valid_idx = np.random.choice(len(rows), self.max_comparison_per_sample)
        # optimize the format later
        return context + self.postfix_prompt, [r for idx, r in enumerate(rows) if idx in valid_idx]
