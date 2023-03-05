"""
    author: theblackcat102

    Dataset output format from __getitem__

     - question / prompt : string

     - answers / rows : list of tuple pair. The first element in the tuple pair must be the positive pair (rank higher than the second element)

    A list of rank based dataset for training using rank loss

    Some nice features to have

    [] support additional negative samples generated from other models.

        For example we can use galactica-125m to generate a TLDR and assume it was
        inferior than the human preference one


"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import numpy as np
import torch
from datasets import load_dataset
from torch.utils.data import Dataset
from transformers.tokenization_utils_base import PaddingStrategy, PreTrainedTokenizerBase


@dataclass
class RankGenCollator:
    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    max_examples: Optional[int] = None

    def __call__(self, batch: List[Dict[str, str]]) -> Dict[str, torch.Tensor]:
        prefixes = []
        better_answers = []
        worse_answers = []
        for question, pairs in batch:
            for pos, neg in pairs:
                prefixes.append("pre " + question)
                better_answers.append("suffi " + pos)
                worse_answers.append("suffi " + neg)

        tokenized_prefixes = self.tokenizer(
            prefixes, return_tensors="pt", padding=self.padding, max_length=self.max_length, truncation=True
        )
        tokenized_pos = self.tokenizer(
            better_answers, return_tensors="pt", padding=self.padding, max_length=self.max_length, truncation=True
        )
        tokenized_neg = self.tokenizer(
            worse_answers, return_tensors="pt", padding=self.padding, max_length=self.max_length, truncation=True
        )
        return {"prefix": tokenized_prefixes, "positive": tokenized_pos, "negative": tokenized_neg}


@dataclass
class DataCollatorForPairRank:
    """

    Data collator that will dynamically pad the inputs for multiple choice received.

    """

    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    drop_token_type: bool = False  # galactica

    def __call__(self, features):
        flatten_features = []
        for question, pairs in features:
            for pos, neg in pairs:
                flatten_features.append(self.tokenizer(question, pos, truncation=True, max_length=self.max_length))
                flatten_features.append(self.tokenizer(question, neg, truncation=True, max_length=self.max_length))
        batch = self.tokenizer.pad(
            flatten_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        if self.drop_token_type:
            batch.pop("token_type_ids")
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

    def __init__(self, split="train", conf_threshold=-1, max_comparison_per_sample=1) -> None:
        super().__init__()
        assert split in ("train", "valid1", "valid2", "test")
        summaries = {}
        # using prompt as our index will allows us
        # to add additional generated prompt later
        self.index2summary = {}
        self.max_comparison_per_sample = max_comparison_per_sample
        major_split = split if "train" == split else "validation"
        dataset = load_dataset("openai/summarize_from_feedback", "comparisons")[major_split]
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


class HFDataset(Dataset):
    """
    This is a base huggingface dataset which written to support the
    simplest pos-neg pair format

    we should do something like this for supervised datasets
    """

    def __init__(
        self, dataset_name, question_field, pos_answer_field, neg_answer_field, subset=None, split=None
    ) -> None:
        super().__init__()
        dataset = load_dataset(dataset_name, subset)
        if split is not None:
            dataset = dataset[split]

        self.questions = {}
        self.index2question = {}
        for row in dataset:
            question = row[question_field].strip()
            pos = row[pos_answer_field]
            neg = row[neg_answer_field]
            if question not in self.index2question:
                self.index2question[len(self.index2question)] = question

            if question not in self.questions:
                self.questions[question] = []
            self.questions[question].append((pos.strip(), neg.strip()))

    def __len__(self):
        return len(self.index2question)

    def __getitem__(self, index):
        question = self.index2question[index]
        rows = self.questions[question]
        # optimize the format later
        return question, rows


class GPTJSynthetic(HFDataset):
    def __init__(self) -> None:
        super().__init__("Dahoas/synthetic-instruct-gptj-pairwise", "prompt", "chosen", "rejected", None, "train")


class AnthropicRLHF(Dataset):
    """
    The data are described in the paper:
        Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback.
        If you find the data useful, please cite the paper.
        The data format is very simple -- each line of the jsonl files contains a pair of texts,
        one "chosen" and one "rejected".
    valid train size : 160780

    """

    def preprocess_dialogue(self, text):
        """
        trim prefix text to last two pairs

        Outlier example Assistant answered empty string:
            Assistant: Human: That makes sense, I agree with that, though there are many situations that
            aren't considered justice, like sending a kid to prison for life.  Human: You are completely
            missing the point of this conversation, and not understanding anything I am saying.  Human:
            And I don’t know if you’re trying to be funny, but it isn’t.

        """
        last_two_convo = text.split("Human:")[-2:]
        if len(last_two_convo[0]) == 0:
            return "Human:".join(last_two_convo)
        return "Human: " + "Human:".join(last_two_convo)

    def __init__(self, split="train", sep_token="<sep>") -> None:
        super().__init__()
        assert split in ("train", "test")
        if sep_token is None:
            sep_token = " . "
        self.pairs = []
        # using prompt as our index will allows us
        # to add additional generated prompt later
        major_split = split if "train" == split else "test"
        dataset = load_dataset("Anthropic/hh-rlhf")[major_split]
        for data in dataset:
            processed = self.preprocess_dialogue(data["chosen"])
            # roughly 20 of these are invalid conversation
            if "Assistant" not in processed:
                continue
            prompt, pos_postfix = processed.split("Assistant:", maxsplit=1)
            prompt = prompt.replace("Human: ", "").strip()
            pos_postfix = pos_postfix.replace("Human: ", sep_token).replace("\n\nAssistant: ", sep_token).strip()
            processed = self.preprocess_dialogue(data["rejected"])
            if "Assistant" not in processed:
                continue
            _, neg_postfix = processed.split("Assistant:", maxsplit=1)
            neg_postfix = neg_postfix.replace("Human: ", sep_token).replace("\n\nAssistant: ", sep_token).strip()
            self.pairs.append((prompt, (pos_postfix.strip(), neg_postfix.strip())))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        context, pair = self.pairs[index]

        return context, [pair]


class OAPrivate(Dataset):
    """
    {
        "prompt": <prompt string>,
        "history": [("prompt1", "answer2"), ("prompt2", "answer2")],
        "pos": <pos answer string>,
        "neg_replies": [list of bad answers]
    }
    """

    split_name_mapping = {
        "train": "rm_train.jsonl",
        "test": "rm_test.jsonl",
        "val": "rm_val.jsonl",
    }

    def __init__(self, split="train", sep_token="<sep>", data_path=".cache") -> None:
        super().__init__()
        import json

        jsonl_file = os.path.join(data_path, self.split_name_mapping[split])
        self.pairs = []
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                prefix = sep_token.join([sep_token.join(p) for p in data["history"][-2:]])
                prefix += sep_token + data["prompt"]
                pair = []
                for neg_text in data["neg_replies"]:
                    pair.append((data["pos"], neg_text))
                self.pairs.append((prefix, pair))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        context, pair = self.pairs[index]

        return context, pair
