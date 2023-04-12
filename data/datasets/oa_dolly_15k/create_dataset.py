import json
from pathlib import Path

import requests
from datasets import Dataset

DATA_URL = "https://raw.githubusercontent.com/databrickslabs/dolly/master/data/databricks-dolly-15k.jsonl"
FILE_PATH = "databricks_dolly_15k.jsonl"


def download_data(url: str, destination: str):
    response = requests.get(url, stream=True)

    with open(destination, "wb") as handle:
        for data in response.iter_content():
            handle.write(data)


def build_dataset(data_file: str, include_context: bool = True) -> Dataset:
    json_data = [
        to_oa_format(json.loads(line), include_context=include_context)
        for line in Path(data_file).read_text().splitlines()
    ]

    dataset = Dataset.from_list(json_data)
    return dataset


def to_oa_format(data: dict, include_context: bool = True) -> dict:
    output_data = {
        "INSTRUCTION": data["instruction"],
        "RESPONSE": data["response"],
        "SOURCE": "databricks-dolly-15k",
        "METADATA": {
            "CATEGORY": data["category"],
        },
    }

    if include_context:
        output_data["METADATA"]["CONTEXT"] = data["context"]

    return output_data


def main():
    download_data(DATA_URL, FILE_PATH)
    dataset = build_dataset(FILE_PATH, include_context=True)
    dataset.push_to_hub("OllieStanley/oa_dolly_15k")


if __name__ == "__main__":
    main()
