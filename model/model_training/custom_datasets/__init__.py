"""
    High level functions for model training
"""
from model_training.custom_datasets.instruction import INSTRUCTION_DATASETS, InstructionDataset
from model_training.custom_datasets.oasst_dataset import load_oasst_export
from model_training.custom_datasets.prompt_dialogue import Gpt4All, load_oig_file
from model_training.custom_datasets.qa_datasets import (
    SODA,
    Alpaca,
    CodeAlpaca,
    JokeExplaination,
    QADataset,
    SODADialogue,
    TranslatedQA,
    WebGPT,
)
from model_training.custom_datasets.summarization import SummarizationDataset
from model_training.custom_datasets.toxic_conversation import ProsocialDialogue, ProsocialDialogueExplaination
from model_training.custom_datasets.translation import WMT2019, DiveMT, TEDTalk
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, Subset

QA_DATASETS = list(QADataset.DATASET_FORMAT_MAPPING.keys())
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
OTHER = ["prosocial_dialogue", "explain_prosocial", "private_tuning", "oa_translated"]

RL_DATASETS = ["webgpt", "private_tuning", "alpaca"]

RM_DATASETS = ["oasst_export"]


def train_val_dataset(dataset, val_split=0.2) -> tuple[Dataset, Dataset | None]:
    if val_split == 0:
        return dataset, None

    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_one_dataset(
    conf, dataset_name, val_split=0.2, data_path=None, mode="sft", **kwargs
) -> tuple[Dataset, Dataset | None]:
    if mode == "rl":
        assert dataset_name in RL_DATASETS, f"Dataset {dataset_name} not supported for RL"

    if mode == "rm":
        assert dataset_name in RM_DATASETS, f"Dataset {dataset_name} not supported for reward modeling"

    data_path = data_path or conf.cache_dir
    dataset_name = dataset_name.lower()

    if dataset_name in QA_DATASETS:
        dataset = QADataset(dataset_name, data_path, "train")
        if not dataset.no_val:
            eval = QADataset(dataset_name, data_path, "validation")
            train = dataset
    elif dataset_name in SUMMARIZATION_DATASETS:
        dataset = SummarizationDataset(dataset_name, data_path, "train")
        if dataset_name != "debate_sum":
            eval = SummarizationDataset(dataset_name, data_path, "validation")
            train = dataset
    elif dataset_name in INSTRUCTION_DATASETS:
        dataset = InstructionDataset(dataset_name, data_path, "train")
    elif "ted_trans" in dataset_name:
        language_pair = dataset_name.split("_")[-1]
        dataset = TEDTalk(pair=language_pair, split="train")
    elif "wmt2019" in dataset_name:
        language_pair = dataset_name.split("_")[-1]
        train = WMT2019(pair=language_pair, split="train")
        eval = WMT2019(pair=language_pair, split="validation")
    elif dataset_name == "dive_mt":
        dataset = DiveMT()
    elif dataset_name == "webgpt":
        dataset = WebGPT()
    elif dataset_name == "alpaca":
        dataset = Alpaca(mode=mode, cache_dir=data_path)
    elif dataset_name == "code_alpaca":
        dataset = CodeAlpaca(mode=mode, cache_dir=data_path)
    elif dataset_name == "gpt4all":
        dataset = Gpt4All(mode=mode, cache_dir=data_path)
    elif dataset_name == "prosocial_dialogue":
        train = ProsocialDialogue(cache_dir=data_path, split="train")
        eval = ProsocialDialogue(cache_dir=data_path, split="validation")
    elif dataset_name == "explain_prosocial":
        train = ProsocialDialogueExplaination(cache_dir=data_path, split="train")
        eval = ProsocialDialogueExplaination(cache_dir=data_path, split="validation")
    elif dataset_name == "soda":
        dataset = SODA(data_path)
    elif dataset_name == "soda_dialogue":
        dataset = SODADialogue(data_path)
    elif dataset_name == "joke":
        dataset = JokeExplaination(data_path)
    elif dataset_name == "oa_translated":
        # TODO make val_split lower..? by saganos
        dataset = TranslatedQA(data_path)
    elif dataset_name == "oasst_export":
        train, eval = load_oasst_export(data_path=data_path, val_split=val_split, mode=mode, **kwargs)
    elif dataset_name == "oig_file":
        train, eval = load_oig_file(val_split=val_split, **kwargs)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")

    # if eval not already defined
    if not ("eval" in locals() and "train" in locals()):
        train, eval = train_val_dataset(dataset, val_split=val_split)

    return train, eval
