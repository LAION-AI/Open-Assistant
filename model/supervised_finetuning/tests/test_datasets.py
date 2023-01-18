from argparse import Namespace

from custom_datasets import QA_DATASETS, SUMMARIZATION_DATASETS, get_one_dataset
from custom_datasets.dialogue_collator import DialogueDataCollator


def test_all_datasets():
    qa_base = QA_DATASETS
    summarize_base = SUMMARIZATION_DATASETS
    others = ["prompt_dialogue", "webgpt", "soda", "joke"]

    config = Namespace(cache_dir=".cache")
    for dataset_name in others + qa_base + summarize_base:
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
    collate_fn = DialogueDataCollator(tokenizer, max_length=512)
    qa_base = QA_DATASETS
    summarize_base = SUMMARIZATION_DATASETS
    others = ["prompt_dialogue", "webgpt", "soda", "joke", "gsm8k"]

    trains, evals = [], []
    for dataset_name in others + qa_base + summarize_base:
        print(dataset_name)
        train, eval = get_one_dataset(config, dataset_name)
        trains.append(train)
        evals.append(eval)

    dataloader = DataLoader(ConcatDataset(trains), collate_fn=collate_fn, batch_size=128)
    for batch in dataloader:
        # print(batch.keys())
        # print(tokenizer.decode(batch['input_ids'][0]))
        # print('-----')
        # print(tokenizer.decode(batch['targets'][0][batch['label_masks'][0]]))
        assert batch["targets"].shape[1] <= 512
    dataloader = DataLoader(ConcatDataset(evals), collate_fn=collate_fn, batch_size=128)
    for batch in dataloader:
        assert batch["targets"].shape[1] <= 512


if __name__ == "__main__":
    test_collate_fn()
