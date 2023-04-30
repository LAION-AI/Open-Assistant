from dataclasses import dataclass
from typing import Dict, List

import torch
from datasets import concatenate_datasets
from torch.utils.data import Dataset

LABEL2ID = {
    "__casual__": "__casual__",
    "__needs_caution__": "__needs_caution__",
    "__needs_intervention__": "__needs_intervention__",
    "__probably_needs_caution__": "__probably_needs_caution__",
    "__possibly_needs_caution__": "__possibly_needs_caution__",
}


class SafetyDataset(Dataset):

    """
    Dataset to train safety model with context and ROT from prosocial-dialog
    input format : input<ctx>context</s>
    output format : <cls>safety_label<rot>ROTs</s>

    """

    def __init__(self, dataset, split, tokenizer, max_len=512):
        super().__init__()

        if isinstance(split, List):
            self.split = "-".join(split)
            self.dataset = concatenate_datasets([dataset[sp] for sp in split])
        else:
            self.split = split
            self.dataset = dataset[split]

        self.max_len = max_len
        self.tokenizer = tokenizer
        self.label2id = LABEL2ID

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        idx_start = idx
        end = self.dataset[max(0, idx_start - 1)]["episode_done"]
        while (not end) and (idx_start > 0):
            end = self.dataset[max(0, idx_start - 2)]["episode_done"]
            idx_start -= 1
        idx_start = max(0, idx_start)
        context = [
            f'\nUser: {self.dataset[i]["context"]}\n bot:{self.dataset[i]["response"]}' for i in range(idx_start, idx)
        ]
        context = self.tokenizer.sep_token.join(context)
        rots = self.dataset[idx]["rots"]
        label = self.label2id[self.dataset[idx]["safety_label"]]
        input_tokens = self.tokenizer.encode(self.dataset[idx]["context"], add_special_tokens=False)
        max_len = self.max_len - (len(input_tokens) + 2)
        context = self.tokenizer.encode(
            context,
            add_special_tokens=False,
            max_length=max_len,
        )
        rots = self.tokenizer.sep_token.join(rots)
        input_ids = input_tokens + [self.tokenizer.context_token_id] + context + [self.tokenizer.eos_token_id]
        input_ids = input_ids + [self.tokenizer.pad_token_id] * max(0, (self.max_len - len(input_ids)))
        mask = [1] * len(input_ids) + [self.tokenizer.pad_token_id] * (self.max_len - len(input_ids))
        target_text = self.tokenizer.label_token + label + self.tokenizer.context_token + rots
        decoder_ids = self.tokenizer(
            target_text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding="max_length",
        )

        return {
            "input_ids": torch.LongTensor(input_ids),
            "attention_mask": torch.LongTensor(mask),
            "decoder_input_ids": torch.LongTensor(decoder_ids["input_ids"]),
            "decoder_attention_mask": torch.LongTensor(decoder_ids["attention_mask"]),
        }


@dataclass
class SafetyDataCollator:
    def __call__(self, batch: List) -> Dict[str, torch.Tensor]:
        """
        Take a list of samples from a Dataset and collate them into a batch.
        Returns:
        A dictionary of tensors
        """

        input_ids = torch.stack([example["input_ids"] for example in batch])
        lm_labels = torch.stack([example["decoder_input_ids"] for example in batch])
        lm_labels[lm_labels[:, :] == 0] = -100
        attention_mask = torch.stack([example["attention_mask"] for example in batch])
        decoder_attention_mask = torch.stack([example["decoder_attention_mask"] for example in batch])

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": lm_labels,
            "decoder_attention_mask": decoder_attention_mask,
        }
