# -*- coding: utf-8 -*-
from experimental_dataset import DataCollatorForSummaryScore, HFSummaryQuality
from rank_datasets import DataCollatorForPairRank, HFSummary, WebGPT
from torch.utils.data import DataLoader
from transformers import AutoTokenizer


def test_hfsummary():

    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForPairRank(tokenizer, max_length=200)
    dataset = HFSummary("train")
    print(len(dataset))
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=8)
    for batch in dataloader:
        batch["input_ids"].shape


def test_webgpt():

    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForPairRank(tokenizer, max_length=200)
    dataset = WebGPT()
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=32)
    for batch in dataloader:
        print(batch["input_ids"].shape)


def test_hf_quality():

    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForSummaryScore(tokenizer, max_length=200)
    dataset = HFSummaryQuality("validation", tokenizer)
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=32)
    for batch in dataloader:
        print(batch["input_ids"].shape)


if __name__ == "__main__":
    test_hf_quality()
    # test_webgpt()
