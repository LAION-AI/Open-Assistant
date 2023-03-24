from argparse import Namespace

import pytest
from model_training.custom_datasets import get_one_dataset
from model_training.custom_datasets.ranking_collator import RankingDataCollator
from model_training.utils import get_tokenizer
from torch.utils.data import DataLoader


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
    print("input_ids[0, :200]", input_ids[0, :200])
    print("decoded input_ids[0, :200]:", tokenizer.decode(input_ids[0, :200]))
    print("decoded non masked input_ids[0]:", tokenizer.decode(input_ids[0][x.attention_mask[0] == 1]))

    print(y)


if __name__ == "__main__":
    test_ranking_collator()
