import json
from pathlib import Path

from datasets import Dataset, load_dataset


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
    dataset = load_dataset("argilla/databricks-dolly-15k-curated-multilingual")
    json_data = []
    for lang, data in dataset.items():
        for row in data:
            json_data.append({
                "INSTRUCTION": row["instruction"],
                "INSTRUCTION_EN": row["instruction_original_en"],
                "RESPONSE_EN": row["response_original_en"],
                "RESPONSE": row["response"],
                "SOURCE": "databricks-dolly-15k-curated-multilingual",
                "METADATA": {
                    "CATEGORY": row["category"],
                    "CONTEXT": row["context"],
                    "LANG": lang
                },
            })
    format_dataset = Dataset.from_list(json_data)
    format_dataset.push_to_hub("blancsw/oa_dolly_15k_multilingual")


if __name__ == "__main__":
    main()
