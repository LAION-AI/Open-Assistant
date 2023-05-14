import json
import random
import re
from dataclasses import dataclass

import pandas as pd
from datasets import load_dataset

random.seed(42)

random_list_python = [
    "Make a python code.",
    "Make a python script. Only function.",
    "Write a solution in python.",
    "Solve with Python.",
    "Please, use python!",
    "Also, could you use python?",
    "Think and write in python.",
    "Write a function in python.",
    "Make a Python function.",
]

random_list_answer = [
    "\nAnswer is",
    "\nThe final answer:",
    "\nThe answer will be",
]


def qna_wrapper(source, random_list_python, random_list_answer):
    def create_qna(row):
        instruction = row["question"] if source == "gsm8k" else row["input"] + " " + random.choice(random_list_python)
        response = (
            re.sub(r"(<<[\d\.\-\+\*=/\\]+>>)", "", row["answer"].replace("####", random.choice(random_list_answer)))
            + "."
            if source == "gsm8k"
            else row["code"]
        )
        metadata = {
            "language": "en",
        }
        metadata_str = json.dumps(metadata)
        return QnA(instruction, response, source, metadata_str)

    return create_qna


@dataclass
class QnA:
    INSTRUCTION: str
    RESPONSE: str
    SOURCE: str
    METADATA: str


# load gsm8k & gsm-hard
dataset1 = load_dataset("gsm8k", "main", split="train")
print(dataset1)

dataset2 = load_dataset("reasoning-machines/gsm-hard", split="train")
print(dataset2)

# process gsm8k & gsm-hard
qna_list_1 = pd.DataFrame(dataset1).apply(qna_wrapper("gsm8k", random_list_python, random_list_answer), axis=1).tolist()
qna_list_2 = (
    pd.DataFrame(dataset2).apply(qna_wrapper("gsm-hard", random_list_python, random_list_answer), axis=1).tolist()
)

# merge gsm8k & gsm-hard
qna_list = qna_list_1 + qna_list_2

# convert to parquet
qna_df = pd.DataFrame(qna_list, columns=["INSTRUCTION", "RESPONSE", "SOURCE", "METADATA"])
qna_df.to_parquet("reasoning-gsm-qna.parquet", row_group_size=100, engine="pyarrow", index=False)
