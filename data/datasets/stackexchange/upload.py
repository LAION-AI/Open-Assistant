#!/usr/bin/env python3
# Simple script to convert StackExchange XML to Open Assistant format
# Original code by https://github.com/b-mc2

from datasets import load_dataset

PARQUET_FILE = "stackexchange.parquet"
HF_DATASET = "donfu/oa-stackexchange"


def upload_hf():
    """
    Upload to Hugging Face. Make sure you are logged in beforehand with `huggingface-cli login`
    """
    parquet_file = PARQUET_FILE
    dataset = load_dataset("parquet", data_files=parquet_file, name="oa-stackexchange")
    dataset.push_to_hub(HF_DATASET, max_shard_size="500MB")
    print("Uploaded to Hugging Face: " + HF_DATASET)


if __name__ == "__main__":
    upload_hf()
