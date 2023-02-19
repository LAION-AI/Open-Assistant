"""
    Summarize different spectrum of documents
"""
import random

from custom_datasets.formatting import format_pair
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
        return format_pair((context, summary))
