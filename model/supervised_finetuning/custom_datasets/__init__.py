"""
    High level functions for model training
"""
from custom_datasets.prompt_dialogue import InstructionTuning, PromptGeneratedDataset
from custom_datasets.qa_datasets import SODA, JokeExplaination, QADataset, SODADialogue, WebGPT
from custom_datasets.summarization import SummarizationDataset
from custom_datasets.toxic_conversation import ProsocialDialogue, ProsocialDialogueExplaination
from custom_datasets.translation import WMT2019, DiveMT, TEDTalk
from sklearn.model_selection import train_test_split
from torch.utils.data import Subset

QA_DATASETS = [
    "squad_v2",
    "adversarial_qa",
    "trivia_qa_context",
    "trivia_qa_nocontext",
    "gsm8k",
    "wikihow",
    "essay_instruction",
    "math_qa",
    "reddit_eli5",
    "reddit_askh",
    "reddit_asks",
]
SUMMARIZATION_DATASETS = [
    "xsum",
    "cnn_dailymail",
    "samsum",
    "multi_news",
    "scitldr",
    "billsum",
    "debate_sum",
    "tldr_news",
]
OTHER = ["prosocial_dialogue", "explain_prosocial", "instruct_tuning"]


def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_one_dataset(conf, dataset_name):
    dataset_name = dataset_name.lower()

    if dataset_name in QA_DATASETS:
        train = QADataset(dataset_name, conf.cache_dir, "train")
        if train.no_val:
            train, eval = train_val_dataset(train, val_split=0.2)
        else:
            eval = QADataset(dataset_name, conf.cache_dir, "validation")
    elif dataset_name in SUMMARIZATION_DATASETS:
        train = SummarizationDataset(dataset_name, conf.cache_dir, "train")
        if dataset_name == "debate_sum":
            train, eval = train_val_dataset(train, val_split=0.2)
        else:
            eval = SummarizationDataset(dataset_name, conf.cache_dir, "validation")
    elif "ted_trans" in dataset_name:
        language_pair = dataset_name.split("_")[-1]
        dataset = TEDTalk(pair=language_pair, split="train")
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif "wmt2019" in dataset_name:
        language_pair = dataset_name.split("_")[-1]
        train = WMT2019(pair=language_pair, split="train")
        eval = WMT2019(pair=language_pair, split="validation")
    elif dataset_name == "dive_mt":
        dataset = DiveMT()
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif dataset_name == "webgpt":
        dataset = WebGPT()
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif dataset_name == "prompt_dialogue":
        dataset = PromptGeneratedDataset(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif dataset_name == "prosocial_dialogue":
        train = ProsocialDialogue(cache_dir=conf.cache_dir, split="train")
        eval = ProsocialDialogue(cache_dir=conf.cache_dir, split="validation")
    elif dataset_name == "explain_prosocial":
        train = ProsocialDialogueExplaination(cache_dir=conf.cache_dir, split="train")
        eval = ProsocialDialogueExplaination(cache_dir=conf.cache_dir, split="validation")
    elif dataset_name == "soda":
        dataset = SODA(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.1)
    elif dataset_name == "soda_dialogue":
        dataset = SODADialogue(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.1)
    elif dataset_name == "joke":
        dataset = JokeExplaination(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.2)
    elif dataset_name == "instruct_tuning":
        dataset = InstructionTuning(conf.cache_dir)
        train, eval = train_val_dataset(dataset, val_split=0.2)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")

    return train, eval
