"""
   Datasets for LM objective pre-training aimed to prevent catastrophic forgetting during fine-tuning
"""
from pathlib import Path
from typing import Optional

from datasets import load_dataset
from model_training.custom_datasets.formatting import DatasetEntryLm
from torch.utils.data import Dataset


class PretrainDataset(Dataset):
    def __init__(
        self,
        dataset_name: str,
        split: str,
        text_column_name: str,
        cache_dir: str | Path,
        mode: str = "sft",
        max_chunk_size: Optional[int] = 64 * 1024,
    ) -> None:
        super().__init__()

        assert mode in ("sft", "rm", "rl")
        self.mode = mode
        self.max_chunk_size = max_chunk_size
        self.dataset = load_dataset(dataset_name, cache_dir=cache_dir)[split]
        self.text_column_name = text_column_name

        # split long entries into chunks smaller than max_chunk_size
        self.index_map = []
        for i, entry in enumerate(self.dataset):
            text_len = len(entry[self.text_column_name])
            for segment_begin in range(0, text_len, max_chunk_size):
                segment_end = min(segment_begin + max_chunk_size, text_len)
                self.index_map.append((i, segment_begin, segment_end))

    def __len__(self) -> int:
        return len(self.index_map)

    def __getitem__(self, index) -> DatasetEntryLm:
        i, segment_begin, segment_end = self.index_map[index]
        text = self.dataset[i][self.text_column_name][segment_begin:segment_end]
        return DatasetEntryLm(text=text)


class RedPajama(PretrainDataset):
    name = "red_pajama"

    def __init__(
        self,
        cache_dir: str | Path,
        mode: str = "sft",
        max_chunk_size: Optional[int] = 64 * 1024,
    ) -> None:
        super().__init__(
            dataset_name="togethercomputer/RedPajama-Data-1T-Sample",
            split="train",
            text_column_name="text",
            cache_dir=cache_dir,
            mode=mode,
            max_chunk_size=max_chunk_size,
        )


class FanFics(PretrainDataset):
    name = "fanfics"

    def __init__(
        self,
        cache_dir: str | Path,
        mode: str = "sft",
        max_chunk_size: Optional[int] = 64 * 1024,
    ) -> None:
        super().__init__(
            dataset_name="atom-in-the-universe/fanfics-10k-50k",
            split="train",
            text_column_name="TEXT",
            cache_dir=cache_dir,
            mode=mode,
            max_chunk_size=max_chunk_size,
        )
