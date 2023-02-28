from experimental_dataset import DataCollatorForSummaryScore, HFSummaryQuality
from rank_datasets import AnthropicRLHF, DataCollatorForPairRank, GPTJSynthetic, HFSummary, WebGPT
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


def test_anthropic_rlhf():
    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForPairRank(tokenizer, max_length=200)
    dataset = AnthropicRLHF("test", sep_token=tokenizer.sep_token)
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=32)
    for batch in dataloader:
        print(batch["input_ids"].shape)


def test_hf_summary_quality():
    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForSummaryScore(tokenizer, max_length=200)
    dataset = HFSummaryQuality("validation", tokenizer)
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=32)
    for batch in dataloader:
        print(batch["input_ids"].shape)


def test_gptj_dataset():
    dataset = GPTJSynthetic()
    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForPairRank(tokenizer, max_length=1024)

    print(len(dataset))
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=32)
    for batch in dataloader:
        batch["input_ids"].shape
