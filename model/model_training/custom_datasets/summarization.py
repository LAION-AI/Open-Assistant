"""
    Summarize different spectrum of documents
"""
import random
from collections import defaultdict

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


class HFSummary(Dataset):
    """
    Human feedback data from OpenAI
    https://github.com/openai/summarize-from-feedback
    https://huggingface.co/datasets/openai/summarize_from_feedback

    labeling method : pair comparison, 0 or 1

    """

    PROMPTS = [
        "Please summarize the following content:\n{}",
        "{}\nTLDR;",
        "{}\nPlease summarize the content above",
        "Write a summary for the following article:\n{}",
    ]

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

            if context not in summaries:
                summaries[context] = []

            pos, neg = (0, 1) if data["choice"] == 0 else (1, 0)
            summaries[context].append((data["summaries"][pos]["text"].strip(), data["summaries"][neg]["text"].strip()))

        ranked_summaries = []
        for context, summary_comparison_pairs in summaries.items():
            if len(summary_comparison_pairs) > 30:
                # outlier example
                continue
            ranks = self.aggregate_pairs(summary_comparison_pairs)
            ranked_summaries.append((context, ranks))
        self.summaries = ranked_summaries

    @staticmethod
    def traverse_dag(reverse_linked_dag, key, depth=0):
        # we want to find all the ancestor of the key:
        # ie ancestor of D are [A, B, C]
        # so we create a reverse linked dag
        if depth > (len(reverse_linked_dag) + 1):
            # cicular rank detected, ignore results
            return []
        output = []
        if key in reverse_linked_dag:
            for element in reverse_linked_dag[key]:
                output.append(element)
                if element in reverse_linked_dag:
                    output += HFSummary.traverse_dag(reverse_linked_dag, element, depth=depth + 1)
        return output

    @staticmethod
    def aggregate_pairs(comparison_pairs):
        # perfect case
        # comparison_pairs = [('B', 'D'), ('A', 'B'), ('C', 'D'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D')]
        # comparison_pairs = [('B', 'C'), ('A', 'B'), ('C', 'D')]
        # comparison_pairs = [('B', 'D'), ('A', 'B'), ('C', 'D')]
        # aggregate_pairs(comparison_pairs) = ['A', 'B', 'C', 'D']
        # A > B > C
        # perfect case:
        # (A, B), (A, C), (B, C)
        # worse case:
        # (A, B), (B, C)
        # A > B = C > D
        # (A, B), (B, D), (A, C), (C, D)
        # TODO: how to handle such case?
        reverse_linked_dag = defaultdict(set)
        for pair in comparison_pairs:
            reverse_linked_dag[pair[1]].add(pair[0])
        node_count = defaultdict(int)
        for key, _ in reverse_linked_dag.items():
            node_count[key]  # make it zero
            for e in HFSummary.traverse_dag(reverse_linked_dag, key):
                node_count[e] += 1
        # those who are referenced the most is the best summary
        # if you want to handle tied results, just find the same frequency
        elements_counts = [(element, count) for element, count in node_count.items()]
        # Sort the list of tuples by count in descending order
        elements_counts.sort(key=lambda x: x[1], reverse=True)
        # Create a list of elements in order of their counts
        sorted_elements = [element for element, _ in elements_counts]
        return sorted_elements

    def __len__(self) -> int:
        return len(self.summaries)

    def __getitem__(self, index) -> tuple | list:
        context, rows = self.summaries[index]
        prompt = random.choice(self.PROMPTS)

        if self.mode == "sft":
            return [prompt.format(context), rows[0]]
        elif self.mode == "rl":
            return (prompt.format(context),)
        elif self.mode == "rm":
            valid_idx = np.random.choice(len(rows), self.max_comparison_per_sample)
            return [prompt.format(context)], [r for idx, r in enumerate(rows) if idx in valid_idx]

        raise RuntimeError(f"Unsupported mode '{self.mode}'")
