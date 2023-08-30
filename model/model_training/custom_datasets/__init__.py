"""
    High level functions for model training
"""
from typing import Optional

import numpy as np
from model_training.custom_datasets.extra_rm_datasets import load_anthropic_rlhf, load_hellaswag, load_shp
from model_training.custom_datasets.instruction import (
    INSTRUCTION_DATASETS,
    RAG_DATASETS,
    InstructionDataset,
    RAGDataset,
)
from model_training.custom_datasets.oasst_dataset import load_oasst_export
from model_training.custom_datasets.pretrain_datasets import FanFics, RedPajama
from model_training.custom_datasets.prompt_dialogue import DolphinMix, Gpt4All, OrcaChat, load_oig_file
from model_training.custom_datasets.qa_datasets import (
    SODA,
    AlpacaGpt4,
    DatabricksDolly15k,
    Dolly15kMultilingual,
    GPTeacher_Roleplay,
    JokeExplaination,
    QADataset,
    SODADialogue,
    TranslatedQA,
    Vicuna,
    WebGPT,
    WizardEvolInstructV2,
    load_alpaca_dataset,
)
from model_training.custom_datasets.rank_datasets import AugmentedOA
from model_training.custom_datasets.summarization import HFSummary, HFSummaryPairs, SummarizationDataset
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

OTHER = [
    "prosocial_dialogue",
    "explain_prosocial",
    "private_tuning",
    "oa_translated",
]

RL_DATASETS = [
    "oasst_export",
    "webgpt",
    "private_tuning",
    "alpaca",
    "hf_summary",
    "hf_summary_pairs",
    "vicuna",
]

RM_DATASETS = [
    "oasst_export",
    "augment_oasst",
    "anthropic_rlhf",
    "hf_summary",
    "hf_summary_pairs",
    "shp",
    "hellaswag",
    "webgpt",
]


def train_val_dataset(dataset, val_split=0.2) -> tuple[Dataset, Dataset | None]:
    if val_split == 0:
        return dataset, None

    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_one_dataset(
    conf,
    dataset_name: str,
    val_split: float = 0.2,
    data_path: str = None,
    mode: str = "sft",
    max_val_set: Optional[int] = None,
    **kwargs,
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
        dataset_args = INSTRUCTION_DATASETS[dataset_name]
        dataset = InstructionDataset(name=dataset_name, cache_dir=data_path, split="train", **(dataset_args | kwargs))
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
        dataset = WebGPT(mode=mode)
    elif dataset_name in ("alpaca", "code_alpaca"):
        train, eval = load_alpaca_dataset(dataset_name, val_split=val_split, cache_dir=data_path, **kwargs)
    elif dataset_name == "gpt4all":
        dataset = Gpt4All(mode=mode, cache_dir=data_path)
    elif dataset_name == "prosocial_dialogue":
        dataset = ProsocialDialogue(cache_dir=data_path, split="train")
    elif dataset_name == "explain_prosocial":
        dataset = ProsocialDialogueExplaination(cache_dir=data_path, split="train")
    elif dataset_name == "soda":
        dataset = SODA(data_path, **kwargs)
    elif dataset_name == "soda_dialogue":
        dataset = SODADialogue(data_path)
    elif dataset_name == "joke":
        dataset = JokeExplaination(data_path)
    elif dataset_name == "oa_translated":
        # TODO make val_split lower..? by saganos
        dataset = TranslatedQA(data_path)
    elif dataset_name == "vicuna":
        dataset = Vicuna(cache_dir=data_path, **kwargs)
    elif dataset_name == "wizard_evol_instruct_v2":
        dataset = WizardEvolInstructV2(cache_dir=data_path, **kwargs)
    elif dataset_name == "oasst_export":
        train, eval = load_oasst_export(data_path=data_path, val_split=val_split, mode=mode, **kwargs)
    elif dataset_name == "hf_summary":
        train = HFSummary(split="train", mode=mode)
        eval = HFSummary(split="valid1", mode=mode)
    elif dataset_name == "hf_summary_pairs":
        train = HFSummaryPairs(split="train", mode=mode)
        eval = HFSummaryPairs(split="valid1", mode=mode)
    elif dataset_name == "augment_oasst":
        # reward model mode only
        assert mode == "rm"
        train = AugmentedOA(data_path + "/" + kwargs["input_file_path"], split="train")
        eval = AugmentedOA(data_path + "/" + kwargs["input_file_path"], split="val")
    elif dataset_name == "oig_file":
        train, eval = load_oig_file(val_split=val_split, **kwargs)
    elif dataset_name == "anthropic_rlhf":
        train, eval = load_anthropic_rlhf()
    elif dataset_name == "shp":
        train, eval = load_shp()
    elif dataset_name == "hellaswag":
        train, eval = load_hellaswag()
    elif dataset_name == "dolly15k":
        dataset = DatabricksDolly15k(cache_dir=data_path, mode=mode, **kwargs)
    elif dataset_name == "dolly15k_multilingual":
        dataset = Dolly15kMultilingual(cache_dir=data_path, mode=mode, **kwargs)
    elif dataset_name == "alpaca_gpt4":
        dataset = AlpacaGpt4(cache_dir=data_path, mode=mode, **kwargs)
    elif dataset_name == "red_pajama":
        dataset = RedPajama(cache_dir=data_path, mode=mode, **kwargs)
    elif dataset_name == "fanfics":
        dataset = FanFics(cache_dir=data_path, mode=mode, **kwargs)
    elif dataset_name == "gpteacher_roleplay":
        dataset = GPTeacher_Roleplay(cache_dir=data_path, mode=mode, **kwargs)
    elif dataset_name == "orca-chat":
        dataset = OrcaChat(cache_dir=data_path, **kwargs)
    elif dataset_name == "dolphin-mix":
        dataset = DolphinMix(cache_dir=data_path, **kwargs)
    elif dataset_name in RAG_DATASETS.keys():
        dataset = RAGDataset(dataset_name, cache_dir=data_path, **kwargs)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")

    # if eval not already defined
    if not ("eval" in locals() and "train" in locals()):
        train, eval = train_val_dataset(dataset, val_split=val_split)

    if eval and max_val_set and len(eval) > max_val_set:
        subset_indices = np.random.choice(len(eval), size=max_val_set, replace=False)
        eval = Subset(eval, subset_indices)

    return train, eval
