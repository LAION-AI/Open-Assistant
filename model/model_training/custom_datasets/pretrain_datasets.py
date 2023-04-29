"""
   Datasets for LM objective pre-training aimed to prevent catastrophic forgetting during fine-tuning
"""
from pathlib import Path

from datasets import load_dataset
from model_training.custom_datasets.formatting import DatasetEntry, PretrainDatasetEntry
from torch.utils.data import Dataset


class RedPajama(Dataset):
    name = "red_pajama"

    def __init__(self, cache_dir: str | Path, mode: str = "sft", char_max_len: str = 9216) -> None:
        super().__init__()
        self.mode = mode
        assert mode in ("sft", "rm", "rl")
        self.char_max_len = char_max_len

        self.dataset = load_dataset("togethercomputer/RedPajama-Data-1T-Sample", cache_dir=cache_dir)["train"]

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, index) -> DatasetEntry:
        dialogue = PretrainDatasetEntry(text=self.dataset[index]["text"][: self.char_max_len])
        return dialogue
