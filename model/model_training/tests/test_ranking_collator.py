from argparse import Namespace

import pytest
from custom_datasets import get_one_dataset
from custom_datasets.ranking_collator import RankingDataCollator
from torch.utils.data import DataLoader
from utils import get_tokenizer


@pytest.mark.skip(reason="cache not populated")
def test_ranking_collator():
    # dummy configuration
    config = Namespace(cache_dir=".cache", model_name="EleutherAI/pythia-70m-deduped")

    # get a tokenizer
    tokenizer = get_tokenizer(config)
    print(type(tokenizer))

    # load oasst dataset
    kwargs = {"lang": "en,es,de,fr", "input_file_path": "2023-03-13_oasst_ready_labels.jsonl.gz", "mode": "rm"}
    train, val = get_one_dataset(conf=config, dataset_name="oasst_export", **kwargs)
    print(len(train))
    a = train[0]

    print(type(a))
    print(len(a))
    print("prefix", a[0])
    print("continuations", a[1])

    # create RankingCollator
    ranking_collator = RankingDataCollator(tokenizer=tokenizer)

    dl = DataLoader(
        train,
        batch_size=4,
        collate_fn=ranking_collator,
        num_workers=1,
        pin_memory=False,
    )

    data_iter = iter(dl)
    b = next(data_iter)
    x, y = b

    input_ids = x.input_ids
    attention_mask = x.attention_mask
    print("input_ids", input_ids.shape)
    print("attention_mask", attention_mask.shape)

    print(y)


if __name__ == "__main__":
    test_ranking_collator()
