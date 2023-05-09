#!/usr/bin/env python3
# Simple script to convert StackExchange XML to Open Assistant format
# Original code by https://github.com/b-mc2

import gc
import glob
import os
import re
import subprocess
import sys

import pandas as pd
from html2text import html2text
from lxml import etree
from tqdm import tqdm

XML_DIR = "./xml"
SOURCE = "stackexchange-{0}"
MAX_ANSWERS = 10
QUESTION_SCORE_TRESHOLD = 0
ANSWER_SCORE_TRESHOLD = 0
PARQUET_FILE = "parquet/{0}.parquet"
MAX_LENGTH = 1000  # max length of question or answer


def main():
    datasets = sys.argv[1:] if len(sys.argv) > 1 else list_cached_datasets()
    for dataset in datasets:
        process_dataset(dataset)


def list_cached_datasets():
    xml_files = glob.glob(f"{XML_DIR}/*.xml")
    datasets = [os.path.splitext(os.path.basename(file))[0] for file in xml_files]
    datasets.sort()
    return datasets


def process_dataset(dataset):
    xml_file = f"{XML_DIR}/{dataset}.xml"
    parquet_file = PARQUET_FILE.format(dataset)
    source = SOURCE.format(dataset)
    if not os.path.exists(xml_file):
        print(f"XML file {xml_file} not found, please download first. Skipping...")
    elif not os.path.exists(parquet_file):
        df = parse_and_convert(xml_file, source)
        save_parquet(df, dataset)
    else:
        print(f"File already converted {xml_file}. Skipping...")


def parse_and_convert(path: str, source: str):
    """
    Parse (very large) XML files with sax parser and load it into a pandas Dataframe
    """
    total_rows = int(subprocess.getoutput(f"grep -c '<row' {path}"))
    print(f"Parsing {total_rows} rows from {path}...")
    columns = "Id PostTypeId Body Title Tags Score AcceptedAnswerId ParentId"
    rows = []
    max_process = 10**6
    processed = 0
    oa_df = pd.DataFrame(columns=["INSTRUCTION", "RESPONSE", "SOURCE", "METADATA"])

    context = etree.iterparse(path, events=("end",))

    for _, element in tqdm(context, total=total_rows):
        if element.tag == "row":
            if len(element.get("Body")) > MAX_LENGTH:
                continue
            rows.append(parse_row(element))
            processed += 1
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]

            if processed % max_process == 0 or processed == total_rows:
                df = pd.DataFrame(rows, columns=columns.split())
                rows = []
                oa = convert_to_oa(df, source)
                oa_df = pd.concat([oa_df, oa])
                del df
                del oa
                gc.collect()

    return oa_df


def parse_row(element):
    return [
        int(element.get("Id")),
        int(element.get("PostTypeId")),
        element.get("Body"),
        element.get("Title", ""),
        element.get("Tags", ""),
        int(element.get("Score", 0)),
        int(element.get("AcceptedAnswerId", 0)),
        int(element.get("ParentId", 0)),
    ]


def convert_to_oa(all, source):
    """
    Convert dataframe to Open Assistant format with INSTRUCTION, RESPONSE, SOURCE, METADATA columns

    Only include questions with an AcceptedAnswerId
    """
    questions = all[all["AcceptedAnswerId"] != 0]
    merged = pd.merge(
        questions,
        all,
        how="inner",
        left_on="AcceptedAnswerId",
        right_on="Id",
        suffixes=("_q", "_a"),
    )

    del all

    merged["INSTRUCTION"] = merged["Title_q"] + "\n" + merged["Body_q"].apply(to_markdown)
    merged["RESPONSE"] = merged["Body_a"].apply(to_markdown)
    merged["SOURCE"] = source
    merged["METADATA"] = merged.apply(create_metadata, axis=1)

    return merged[["INSTRUCTION", "RESPONSE", "SOURCE", "METADATA"]]


def convert_tags(raw):
    return raw.replace("-", " ").replace("><", ", ").replace("<", "").replace(">", "")


def create_metadata(row):
    return {
        "tags": convert_tags(row["Tags_q"]),
        "question_score": row["Score_q"],
        "answer_score": row["Score_a"],
    }


def save_parquet(df, dataset):
    """
    Save Dataframe to Parquet. See here for specs:
    https://projects.laion.ai/Open-Assistant/docs/data/datasets#creating-a-dataset-on-hugging-face
    """
    os.makedirs("parquet", exist_ok=True)
    parquet_file = PARQUET_FILE.format(dataset)
    df.to_parquet(parquet_file, row_group_size=100, engine="pyarrow", index=False)
    print(f"Converted {len(df)} instructions into {parquet_file}")


remove_markdown_links_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
remove_remaining_links = r"https?:\/\/[^\s]+"


def remove_emojis(string):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", string)


# Replace HTML content to markdown but remove links
def to_markdown(text):
    try:
        text = html2text(text, bodywidth=0).strip()
    except Exception as e:
        print(e)
        text = re.sub(r"<[^>]*>", "", str(text))
    text = re.sub(remove_markdown_links_pattern, r"\1", text)
    text = remove_emojis(text)
    return re.sub(remove_remaining_links, "", text)


if __name__ == "__main__":
    main()
