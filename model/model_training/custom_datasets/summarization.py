"""
    Summarize different spectrum of documents
"""
import random

import numpy as np
from datasets import load_dataset
from torch.utils.data import Dataset

SUMMARIZATION_SPECIAL_TOKENS = {"Text": "", "Summary": ["TL;DR:", "Summarize this", "Give me the summary"]}

SUMMARY_SPECIAL_PROMPT = {
    "multi_news": ["Summarize in bullet points", "Generate summary in list of points"],
    "xsum": ["Give me summary in one sentence", "Short TLDR", "Give me a concise summary"],
    "samsum": ["TLDR;", "Summarize this dialogue", "Summarize dialogue"],
}

summarization_config_mapping = {
    "cnn_dailymail": (
        "cnn_dailymail",
        "3.0.0",
    ),
    "samsum": ("samsum",),
    "xsum": ("xsum",),
    "multi_news": ("multi_news",),
    "scitldr": (
        "scitldr",
        "AIC",
    ),
    "billsum": ("billsum",),
    "reddit": ("reddit",),
    "tldr_news": ("JulesBelveze/tldr_news",),  # need to fix : JulesBelveze/tldr_news
    "debate_sum": ("Hellisotherpeople/DebateSum",),  # Hellisotherpeople/DebateSum
}

summarization_name_mapping = {
    "cnn_dailymail": ("article", "highlights"),
    "samsum": ("dialogue", "summary"),
    "xsum": ("document", "summary"),
    "multi_news": ("document", "summary"),
    "scitldr": ("source", "target"),
    "billsum": ("text", "summary"),
    "reddit": ("content", "summary"),
    "tldr_news": ("content", "headline"),
    "debate_sum": ("Full-Document", "Extract"),
}


def index_summary_default(text, summary):
    return text.replace("\n\n", "\n"), summary


def index_summary_merge(text, summary):
    return " ".join(text), " ".join(summary)


class SummarizationDataset(Dataset):
    def __init__(self, dataset, cache_dir, split, max_words=512):
        self.name = dataset
        if (dataset in ["billsum", "tldr_news"]) and (split == "validation"):
            split = "test"
        self.dataset = load_dataset(*summarization_config_mapping[dataset], cache_dir=cache_dir, split=split)
        self.text_column, self.summary_column = summarization_name_mapping[dataset]
        self.preprocess_fn = index_summary_merge if dataset == "scitldr" else index_summary_default
        self.max_words = max_words

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        data = self.dataset[idx]
        text, summary = data[self.text_column], data[self.summary_column]
        text, summary = self.preprocess_fn(text, summary)
        if self.name in SUMMARY_SPECIAL_PROMPT:
            prompt = random.choice(SUMMARIZATION_SPECIAL_TOKENS["Summary"])
        else:
            prompt = random.choice(SUMMARIZATION_SPECIAL_TOKENS["Summary"])

        context = "".join([SUMMARIZATION_SPECIAL_TOKENS["Text"], " ".join(text.split(" ")[: self.max_words]), prompt])
        return (context, summary)


SUMMARIZATION_PROMPTS = [
    "Please summarize the following content:\n{}",
    "Write me a summary for the following article:\n{}",
    "Kindly sum up the following information: {}",
    "Please summarize the following text for me:\n{}",
    "Give me a summary of the following text:\n\n{}",
    "Describe the following information in brief: {}",
    "Will you kindly summarize the following paragraph for me?\n{}",
    "Summarize this: {}",
    "TLDR this: {}",
    "{}\nTLDR;",
    "{}\n\nTL;DR",
    "{} tl;dr:",
    "{}\nPlease summarize the content above",
    "{} Please summarize the preceding statements.",
]


class HFSummaryPairs(Dataset):
    """
    Simplified version of the HFSummary class which uses the original examples
    of the OpenAI dataset.
    https://huggingface.co/datasets/openai/summarize_from_feedback
    """

    def __init__(self, split="train", mode="sft", conf_threshold=-1) -> None:
        super().__init__()
        assert split in ("train", "valid1", "valid2", "test")
        assert mode in ("sft", "rm", "rl")
        self.mode = mode

        self.posts = []
        self.summary_pairs = []

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

            self.posts.append(context)
            pos, neg = (0, 1) if data["choice"] == 0 else (1, 0)
            self.summary_pairs.append((data["summaries"][pos]["text"].strip(), data["summaries"][neg]["text"].strip()))

    def __len__(self) -> int:
        return len(self.posts)

    def __getitem__(self, index: int) -> tuple | list:
        if index < 0 or index >= len(self.posts):
            raise IndexError()

        context = self.posts[index]
        # return pairs of comparison
        good_summary, bad_summary = self.summary_pairs[index]
        prompt = random.choice(SUMMARIZATION_PROMPTS)

        # pair very big
        # we are going to do some sampling
        # not optimal but good for now
        if self.mode == "sft":
            return [prompt.format(context), good_summary]
        elif self.mode == "rl":
            return (prompt.format(context),)
        elif self.mode == "rm":
            return [prompt.format(context)], [good_summary, bad_summary]

        raise RuntimeError(f"Unsupported mode '{self.mode}'")


class HFSummary(Dataset):
    """
    Human feedback data from OpenAI
    https://github.com/openai/summarize-from-feedback
    https://huggingface.co/datasets/openai/summarize_from_feedback

    labeling method : pair comparison, 0 or 1

    """

    def __init__(self, split="train", mode="sft", conf_threshold=-1, max_comparison_per_sample=5) -> None:
        super().__init__()
        assert split in ("train", "valid1", "valid2", "test")
        assert mode in ("sft", "rm", "rl")
        self.mode = mode
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
            summaries[context].append((data["summaries"][pos]["text"].strip(), data["summaries"][neg]["text"].strip()))

        ranked_summaries = {}
        for context, summary_comparison_pairs in summaries.items():
            ranks = self.get_sorted_ranks(summary_comparison_pairs)
            ranked_summaries[context] = ranks
        self.summaries = ranked_summaries

    @staticmethod
    def get_sorted_ranks(comparison_pairs):
        # Create a dictionary to keep track of the counts of each element

        counts = {}
        for pair in comparison_pairs:
            if pair[0] not in counts:
                counts[pair[0]] = 0
            if pair[1] not in counts:
                counts[pair[1]] = 0
            counts[pair[0]] += 1

        # Create a list of tuples, where each tuple contains an element and its count
        elements_counts = [(element, count) for element, count in counts.items()]

        # Sort the list of tuples by count in descending order
        elements_counts.sort(key=lambda x: x[1], reverse=True)

        # Create a list of elements in order of their counts
        sorted_elements = [element for element, count in elements_counts]

        return sorted_elements

    def __len__(self) -> int:
        return len(self.index2summary)

    def __getitem__(self, index) -> tuple | list:
        if index < 0 or index >= len(self.index2summary):
            raise IndexError()

        context = self.index2summary[index]
        # return pairs of comparison
        rows = self.summaries[context]
        prompt = random.choice(SUMMARIZATION_PROMPTS)

        # pair very big
        # we are going to do some sampling
        # not optimal but good for now
        if self.mode == "sft":
            return [prompt.format(context), rows[0]]
        elif self.mode == "rl":
            return (prompt.format(context),)
        elif self.mode == "rm":
            valid_idx = np.random.choice(len(rows), self.max_comparison_per_sample)
            return [prompt.format(context)], [r for idx, r in enumerate(rows) if idx in valid_idx]

        raise RuntimeError(f"Unsupported mode '{self.mode}'")
