import json
from dataclasses import dataclass

import pandas as pd
from datasets import concatenate_datasets, load_dataset

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
    instruction = f'{row["question"]} {", ".join(row["answers"])}?'
    response = row["correct"].translate(str.maketrans("", "", "();"))
    source = "reasoning_bg"
    metadata = {
        "language": "bg",
        "url": f'{row["url"]}',
        "id": f'{row["id"]}',
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
