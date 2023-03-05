from argparse import Namespace

from custom_datasets import QA_DATASETS, SUMMARIZATION_DATASETS, get_one_dataset
from custom_datasets.dialogue_collator import DialogueDataCollator
from custom_datasets.prompt_dialogue import OAPrivate, PrivateInstructionTuning


def test_rl_sft_mode_switch():
    dataset = OAPrivate(".cache", split="sft")
    row = dataset[0]
    assert isinstance(row, list)
    dataset = OAPrivate(".cache", split="rl")
    row = dataset[0]
    assert isinstance(row, str)

    dataset = PrivateInstructionTuning(".cache", split="sft")
    row = dataset[0]
    assert isinstance(row, tuple)
    dataset = PrivateInstructionTuning(".cache", split="rl")
    row = dataset[0]
    assert isinstance(row, str)


def test_all_datasets():
    qa_base = QA_DATASETS
    summarize_base = SUMMARIZATION_DATASETS
    others = ["webgpt", "soda", "joke", "explain_prosocial", "prosocial_dialogue"]
    translation = ["dive_mt", "wmt2019_zh-en", "wmt2019_ru-en", "ted_trans_de-ja", "ted_trans_nl-en"]

    config = Namespace(cache_dir=".cache")
    for dataset_name in translation + others + summarize_base + qa_base:
        print(dataset_name)
        train, eval = get_one_dataset(config, dataset_name)
        # sanity check
        for idx in range(min(len(train), 1000)):
            train[idx]
        for idx in range(min(len(eval), 1000)):
            eval[idx]


def test_collate_fn():
    from torch.utils.data import ConcatDataset, DataLoader
    from utils import get_tokenizer

    config = Namespace(cache_dir=".cache", model_name="Salesforce/codegen-2B-multi")
    tokenizer = get_tokenizer(config)
    collate_fn = DialogueDataCollator(tokenizer, max_length=620)
    qa_base = QA_DATASETS
    summarize_base = SUMMARIZATION_DATASETS
    others = ["webgpt", "soda", "joke", "gsm8k"]
    trains, evals = [], []
    for dataset_name in others + qa_base + summarize_base:
        print(dataset_name)
        train, eval = get_one_dataset(config, dataset_name)
        trains.append(train)
        evals.append(eval)

    dataloader = DataLoader(ConcatDataset(trains), collate_fn=collate_fn, batch_size=128)
    for batch in dataloader:
        print(batch["targets"].shape[0])
        print(tokenizer.decode(batch["input_ids"][0]))
        print("-----")
        print(tokenizer.decode(batch["targets"][0][batch["label_masks"][0]]))
        assert batch["targets"].shape[1] <= 620
    dataloader = DataLoader(ConcatDataset(evals), collate_fn=collate_fn, batch_size=128)
    for batch in dataloader:
        assert batch["targets"].shape[1] <= 620
