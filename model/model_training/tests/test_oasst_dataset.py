from argparse import Namespace

from custom_datasets import get_one_dataset


def test_load_oasst_export_dataset():
    config = Namespace(
        cache_dir=".cache",
    )
    kwargs = {
        "lang": "en,es,de,fr",
        "top_k": 2,
        "input_file_path": "2023-02-19_oasst_ready_with_spam_deleted.jsonl.gz",
    }
    print("taeiae")
    train, val = get_one_dataset(conf=config, dataset_name="oasst_export", **kwargs)
    assert len(train) > 9000
    assert len(val) > 2000
