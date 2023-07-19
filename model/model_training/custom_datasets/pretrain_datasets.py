"""
   Datasets for LM objective pre-training aimed to prevent catastrophic forgetting during fine-tuning
"""
import random
from pathlib import Path
from typing import Optional

from datasets import load_dataset
from model_training.custom_datasets.formatting import DatasetEntryLm
from torch.utils.data import Dataset


class RedPajama(Dataset):
    name = "red_pajama"

    def __init__(
        self,
        cache_dir: str | Path,
        mode: str = "sft",
        char_max_len: Optional[int] = 65536,
        random_offset: bool = False,
    ) -> None:
        super().__init__()
        self.mode = mode
        assert mode in ("sft", "rm", "rl")
        self.char_max_len = char_max_len
        self.random_offset = random_offset
        self.dataset = load_dataset("togethercomputer/RedPajama-Data-1T-Sample", cache_dir=cache_dir)["train"]

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, index) -> DatasetEntryLm:
        text = self.dataset[index]["text"]
        if self.char_max_len and len(text) > self.char_max_len:
            offset = 0 if not self.random_offset else random.randrange(len(text) - self.char_max_len)
            text = text[offset : offset + self.char_max_len]
        return DatasetEntryLm(text=text)


class FanFics(Dataset):
    name = "fanfics"

    def __init__(
        self,
        cache_dir: str | Path,
        mode: str = "sft",
        char_max_len: Optional[int] = 65536,
        random_offset: bool = False,
    ) -> None:
        super().__init__()
        self.mode = mode
        assert mode in ("sft", "rm", "rl")
        self.char_max_len = char_max_len
        self.random_offset = random_offset
        self.dataset = load_dataset("atom-in-the-universe/fanfics-10k-50k", cache_dir=cache_dir)["train"]

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, index) -> DatasetEntryLm:
        text = self.dataset[index]["TEXT"]
        if self.char_max_len and len(text) > self.char_max_len:
            offset = 0 if not self.random_offset else random.randrange(len(text) - self.char_max_len)
            text = text[offset : offset + self.char_max_len]
        return DatasetEntryLm(text=text)
