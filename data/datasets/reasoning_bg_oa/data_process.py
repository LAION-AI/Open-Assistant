from datasets import load_dataset, concatenate_datasets
from dataclasses import dataclass
import pandas as pd

import json

configs = ["biology-12th", "philosophy-12th", "geography-12th", "history-12th", "history-quiz"]
datasets = []

@dataclass
class QnA:
    INSTRUCTION: str
    RESPONSE: str
    SOURCE: str
    METADATA: str

# format in QnA
def create_qna(row):
    instruction = row["question"] + " " + ", ".join(row["answers"]) + "?"
    response = row["correct"].translate(str.maketrans("", "", "();"))
    source = "reasoning_bg"
    url = row["url"]
    id_str = row["id"]
    metadata = {
        "language": f"bg",
        "url": f"{url}",
        "id": f"{id_str}",
    }
    metadata_str = json.dumps(metadata)
    return QnA(instruction, response, source, metadata_str)

# merge dataset configs into one
for config in configs:
    dataset = load_dataset("reasoning_bg", config, split="train")
    datasets.append(dataset)

merged_dataset = concatenate_datasets(datasets)

print(merged_dataset)

# convert the dataset to a pandas dataframe
df = pd.DataFrame(merged_dataset)

qna_list = df.apply(create_qna, axis=1).tolist()

qna_df = pd.DataFrame(qna_list, columns=["INSTRUCTION", "RESPONSE", "SOURCE", "METADATA"])
qna_df.to_parquet("reasoning-bg-oa.parquet", row_group_size=100, engine="pyarrow", index=False)
