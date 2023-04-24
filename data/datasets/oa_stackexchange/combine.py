#!/usr/bin/env python3
# Combine (and shorten) parquet files into a single file

import glob

import pandas as pd
from merge_parquets import merge_parquet_dir

MAX_LENGTH = 1000  # max length of question or answer

for file in glob.glob("full/*.parquet"):
    df = pd.read_parquet(file)
    before = len(df)
    df = df[df["INSTRUCTION"].str.len() < MAX_LENGTH]
    df = df[df["RESPONSE"].str.len() < MAX_LENGTH]
    df["METADATA"] = df["METADATA"].apply(
        lambda meta: {
            "tags": meta["tags"],
            "answer_score": int(meta["answer_score"]) if "answer_score" in meta and meta["answer_score"] else 0,
            "question_score": int(meta["question_score"]) if "question_score" in meta and meta["question_score"] else 0,
        }
    )
    df.to_parquet(file)
    after = len(df)
    print(f"Shortened {file} from {before} to {after} rows ({100 * after / before:.2f})")

merge_parquet_dir("full", "stackexchange.parquet")
