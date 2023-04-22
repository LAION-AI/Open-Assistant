from argparse import Namespace

import pytest
from model_training.custom_datasets import get_one_dataset
from model_training.custom_datasets.formatting import QA_SPECIAL_TOKENS  # , DatasetEntry
from model_training.custom_datasets.ranking_collator import RankingDataCollator
from model_training.utils import get_tokenizer, match_tokenizer_name
from torch.utils.data import DataLoader
from transformers.models.auto.tokenization_auto import AutoTokenizer


@pytest.fixture
def pythia_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained("tests/resources/data_collator", local_files_only=True)
    # for this test we use the pythia special tokens but note that this test is model agnostic
    tokenizer_config = match_tokenizer_name("pythia")

    tokenizer.add_special_tokens(
        {
            "pad_token": tokenizer_config.special_tokens.pad_token,
            "eos_token": tokenizer_config.special_tokens.eos_token,
            "sep_token": tokenizer_config.special_tokens.sep_token,
        }
    )

    additional_special_tokens = list(QA_SPECIAL_TOKENS.values())

    tokenizer.add_special_tokens({"additional_special_tokens": additional_special_tokens})
    return tokenizer


def test_ranking_collator_local(pythia_tokenizer):
    first_messages = ["First Instruction."]
    first_replies = [
        "Response A to First Instruction",
        "Response B to First Instruction",
        "First Response C to First Instruction",
    ]
    second_messages = ["Second Instruction."]
    second_replies = ["Response A to Second Instruction", "Response B to Second Instruction"]
    examples = [(first_messages, first_replies), (second_messages, second_replies)]
    rdc = RankingDataCollator(tokenizer=pythia_tokenizer, padding=True)
    batch, cu_lens = rdc(examples=examples)
    eos = pythia_tokenizer.eos_token
    pad = pythia_tokenizer.pad_token
    assert len(batch) == 2
    assert cu_lens == [0, len(first_replies), len(first_replies) + len(second_replies)]
    assert batch.data["attention_mask"].shape[0] == 5  # we have 5 replies in total
    assert batch.data["input_ids"].shape == batch.data["attention_mask"].shape
    # check each instruction
    assert (
        pythia_tokenizer.decode(batch.data["input_ids"][0])
        == f"{QA_SPECIAL_TOKENS['Question']}{first_messages[0]}{eos}{QA_SPECIAL_TOKENS['Answer']}{first_replies[0]}{eos}"
        + 5 * pad
    )
    assert (
        pythia_tokenizer.decode(batch.data["input_ids"][1])
        == f"{QA_SPECIAL_TOKENS['Question']}{first_messages[0]}{eos}{QA_SPECIAL_TOKENS['Answer']}{first_replies[1]}{eos}"
        + 5 * pad
    )
    assert (
        pythia_tokenizer.decode(batch.data["input_ids"][2])
        == f"{QA_SPECIAL_TOKENS['Question']}{first_messages[0]}{eos}{QA_SPECIAL_TOKENS['Answer']}{first_replies[2]}{eos}"
    )

    # todo: add masking


@pytest.mark.skip(reason="manual")
def test_rm_datasets():
    # dummy configuration
    config = Namespace(cache_dir=".cache", model_name="EleutherAI/pythia-70m-deduped")

    dataset_names = ["anthropic_rlhf", "hf_summary_pairs", "webgpt", "hellaswag", "shp", "hf_summary"]
    for name in dataset_names:
        train, val = get_one_dataset(conf=config, dataset_name=name, mode="rm")
        print(f"dataset: '{name}' (train ({type(train)}): {len(train)}, val({type(val)}): {len(val)})")

        avg_number_continuations = sum(len(x[1]) for x in train) / len(train)
        num_more_than_two = sum(1 if len(x[1]) > 2 else 0 for x in train)
        print(f"Average number of continuations: {avg_number_continuations} (with >2: {num_more_than_two})")

        for i in range(10):
            item = train[i + 100]
            print(f"[{i}] Prefix: {item[0]}")
            continuations = item[1]
            print(f"[{i}] Continuations ({len(continuations)}):")
            for j, c in enumerate(continuations):
                print(f"[{i}.{j}]: {c}")


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
    test_rm_datasets()
    # test_ranking_collator()
