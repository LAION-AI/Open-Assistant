import numpy as np
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, Subset

from .prompt_dialogue import PromptGeneratedDataset

QA_SPECIAL_TOKENS = {"Question": "<question>", "Answer": "<answer>"}
SUMMARIZATION_SPECIAL_TOKENS = {"Text": "", "Summary": "TL;DR:"}

summarization_name_mapping = {
    "cnn_dailymail": ("article", "highlights"),
    "samsum": ("dialogue", "summary"),
    "xsum": ("document", "summary"),
    "multi_news": ("document", "summary"),
    "scitldr": ("source", "target"),
    "billsum": ("text", "summary"),
    "reddit": ("content", "summary"),
}
summarization_config_mapping = {
    "cnn_dailymail": ("3.0.0",),
    "samsum": (),
    "xsum": (),
    "multi_news": (),
    "scitldr": ("AIC",),
    "billsum": (),
    "reddit": (),
}

QA_DATASETS = ["squad_v2", "adversarial_qa", "trivia_qa_context", "trivia_qa_noconext"]
SUMMARIZATION_DATASETS = ["xsum", "cnn_dailymail", "samsum", "multi_news"]


def index_squad_v2(example):
    return example["title"] + ". " + example["context"] + " " + example["question"], example["answers"]["text"][0]


def index_trivia_qa_nocontext(example):
    # dummy return one randomly
    return example["question"], example["answer"]["aliases"][np.random.randint(len(example["answer"]["aliases"]))]


def index_trivia_qa_context(example):
    question = example["question"]
    title = example["title"][np.random.randint(len(example["title"]))]
    context = example["search_context"][np.random.randint(len(example["search_context"]))]
    answer = example["answer"]["aliases"][np.random.randint(len(example["answer"]["aliases"]))]

    return title + ". " + context + " " + question, answer


def index_adversarial_qa(example):
    return example["title"] + ". " + example["context"] + " " + example["question"], example["answers"]["text"][0]


class QADataset(Dataset):
    def __init__(self, dataset, cache_dir, split):
        if dataset == "squad_v2":
            self.index_fn = index_squad_v2
            self.dataset = load_dataset("squad_v2", cache_dir=cache_dir, split=split)
        elif dataset == "trivia_qa_nocontext":
            self.index_fn = index_trivia_qa_nocontext
            self.dataset = load_dataset("trivia_qa", "rc.nocontext")
        elif dataset == "trivia_qa_context":
            self.index_fn = index_trivia_qa_context
            self.dataset = load_dataset("trivia_qa", "rc")
        elif dataset == "adversarial_qa":
            self.index_fn = index_adversarial_qa
            self.dataset = load_dataset("adversarial_qa", "adversarialQA")
        else:
            raise ValueError("Unknown dataset : " + dataset)

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        data = self.dataset[idx]
        return self.index_fn(data)


def index_summary_default(text, summary):
    return text, summary


def index_summary_merge(text, summary):
    return " ".join(text), " ".join(summary)


class SummarizationDataset(Dataset):
    def __init__(self, dataset, cache_dir, split):
        self.dataset = load_dataset(dataset, *summarization_config_mapping[dataset], cache_dir=cache_dir, split=split)
        self.summary_column, self.text_column = summarization_name_mapping[dataset]
        self.preprocess_fn = index_summary_merge if dataset == "scitdlr" else index_summary_merge

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        data = self.dataset[idx]
        text, summary = data[self.text_column], data[self.summary_column]
        text, summary = self.preprocess_fn(text, summary)

        return "".join(
            SUMMARIZATION_SPECIAL_TOKENS["Text"], text, " ", SUMMARIZATION_SPECIAL_TOKENS["Summary"], summary
        )


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

            # only keep the best answer
            questions[question] = row["answer_0" if row["score_0"] > row["score_1"] else "answer_1"]

        self.questions = questions

    def __len__(self):
        return len(self.index2question)

    def __getitem__(self, index):
        question = self.index2question[index]
        answer = self.questions[question]
        return [question, answer]


def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_one_dataset(conf, dataset_name):
    dataset_name = dataset_name.lower()

    if dataset_name in ["squad_v2", "adversarial_qa", "trivia_qa_context", "trivia_qa_noconext"]:
        train = QADataset(dataset_name, conf.cache_dir, "train")
        eval = QADataset(dataset_name, conf.cache_dir, "validation")

    elif dataset_name in ["xsum", "cnn_dailymail", "samsum", "multi_news", "scitldr", "billsum", "reddit"]:
        train = SummarizationDataset(dataset_name, conf.cache_dir, "train")
        eval = SummarizationDataset(dataset_name, conf.cache_dir, "validation")

    elif dataset_name == "webgpt":
        dataset = WebGPT()
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif dataset_name == "prompt_dialogue":
        dataset = PromptGeneratedDataset()
        train, eval = train_val_dataset(dataset, val_split=0.2)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")

    return train, eval
