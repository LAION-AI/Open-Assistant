"""Convert the source TSSB-3M  dataset to instruction data
"""

import json
import re
from os.path import join

from tqdm import tqdm

TEMPLATE = """User: Find the bug in the following code:
{}
Reply: The fixed code is:
```
{}
```
"""


# template for pretty output(multiple lines with `User:` & `Reply`)
TEMPLATE_COMMIT_MSG = """User: Find the bug in the following code:
{}
Reply: The bugfix can be described as follows:
{}
The fixed code is:
```
{}
```
"""

INSTRUCTON_TEMPLATE = """Find the bug in the following code:
{}
"""


# template for json output(value)

RESPONSE_TEMPLATE = """The fixed code is:
```
{}
```
"""

RESPONSE_TEMPLATE_COMMIT_MSG = """The bugfix can be described as follows:
{}

The fixed code is:
```
{}
```
"""


def remove_starting_plus_minus(text):
    if text.startswith("+") or text.startswith("-"):
        return text[1:]
    else:
        return text


def remove_extraneous_diff_info(text):
    pattern = "@@.*@@"
    return re.sub(pattern, "", text)


def clean(text):
    return remove_extraneous_diff_info(remove_starting_plus_minus(text))


def clean_commit_msg(text):
    """
    # remove issue id , eg. msg: "rename (hetr_passes -> passes) #1195" -> "rename (hetr_passes -> passes)"
    # remove `fix` prefix:
    ##  eg. [fix] 拼写错误 -> 拼写错误
    ## eg. [FIX] purchase_indonesia : AttributeError 'NoneType' object has no attribute 'id' ->  AttributeError 'NoneType' object has no attribute 'id'
    """
    # Remove issue id
    # pattern = "#\d{1,6}|[fix]|[FIX]"
    pattern = r"#\d{1,6}"
    text = re.sub(pattern, "", text)
    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def create(input_file, output_file, output_json=True):
    fout = open(output_file, "w")
    with open(input_file) as fin:
        for line in tqdm(fin):
            row = json.loads(line.strip())
            wrong = "\n".join(clean(line) for line in row["diff"].split("\n") if not line.startswith("+"))
            correct = "\n".join(clean(line) for line in row["diff"].split("\n") if not line.startswith("-"))

            instruction = INSTRUCTON_TEMPLATE.format(wrong, correct)

            if "commit_message" in row:
                commit_msg = clean_commit_msg(row["commit_message"])
                out_str = TEMPLATE_COMMIT_MSG.format(wrong, commit_msg, correct)
                response = RESPONSE_TEMPLATE_COMMIT_MSG.format(commit_msg, correct)
            else:
                out_str = TEMPLATE.format(wrong, correct)
                response = RESPONSE_TEMPLATE.format(correct)

            if output_json:
                row = {
                    "INSTRUCTION": instruction,
                    "RESPONSE": response,
                    "SOURCE": "TSSM-3M",
                    "METADATA": {
                        "project_url": row["project_url"],
                        "file_path": row["file_path"],
                        "commit_sha": row["commit_sha"],
                    },
                }
                out_str = json.dumps(row, ensure_ascii=False)

            print(out_str, file=fout)
        fout.close()


if __name__ == "__main__":
    """
    # get source data
     !wget https://huggingface.co/datasets/zirui3/TSSB-3M-ext/blob/main/data.jsonl.gz
     !gzip -d data.jsonl.gz
    """

    data_dir = "."
    # source TSSB-3M data
    input_file = join(data_dir, "data.jsonl")
    output_file = join(data_dir, "instructions.json")

    # create(input_file, output_file, output_json=False)
    create(input_file, output_file, output_json=True)
