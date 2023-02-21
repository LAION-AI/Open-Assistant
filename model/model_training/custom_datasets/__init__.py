"""
    High level functions for model training
"""
from custom_datasets.prompt_dialogue import InstructionTuning, OAPrivate, PrivateInstructionTuning
from custom_datasets.qa_datasets import SODA, JokeExplaination, QADataset, SODADialogue, TranslatedQA, WebGPT
from custom_datasets.summarization import SummarizationDataset
from custom_datasets.toxic_conversation import ProsocialDialogue, ProsocialDialogueExplaination
from custom_datasets.translation import WMT2019, DiveMT, TEDTalk
from sklearn.model_selection import train_test_split
from torch.utils.data import Subset

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
OTHER = ["prosocial_dialogue", "explain_prosocial", "instruct_tuning", "private_tuning", "oa_translated", "oa_private"]

RL_DATASETS = ["oa_private"]


def train_val_dataset(dataset, val_split=0.2):
    if val_split == 0:
        return dataset, None

    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_one_dataset(conf, dataset_name, val_split=0.2, data_path=None, mode="sft", **kwargs):
    if mode == "rl":
        assert dataset_name in RL_DATASETS, f"Dataset {dataset_name} not supported for RL"

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
    elif dataset_name == "instruct_tuning":
        dataset = InstructionTuning(data_path)
    elif dataset_name == "private_tuning":
        dataset = PrivateInstructionTuning(data_path)
    elif dataset_name == "oa_translated":
        dataset = TranslatedQA(data_path)  # TODO make val_split lower..?
    elif dataset_name == "oa_private":
        dataset = OAPrivate(data_path, **kwargs)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")

    # if eval not already defined
    if "dataset" in locals():
        train, eval = train_val_dataset(dataset, val_split=val_split)

    return train, eval
