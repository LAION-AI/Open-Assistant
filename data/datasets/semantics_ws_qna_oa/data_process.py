import json
import random
from dataclasses import dataclass

import pandas as pd
import random_stuff
from datasets import load_dataset

random.seed(42)


# format to QnA
def qna_wrapper():
    def create_qna(row):
        # make a random number
        random_num = random.randint(0, 2)

        # extract rows' vals
        lang = row["Language"]
        con_type = row["Type"]
        word1 = row["Word1"]
        word2 = row["Word2"]

        score_percent = row["Score"]
        # 0 - yes; 1 - 50%, 2 - no
        instruction = random_stuff.qna_random_magic(lang, word1, word2, con_type, score_percent, random_num, True)
        response = random_stuff.qna_random_magic(lang, word1, word2, con_type, score_percent, random_num, False)
        source = "WordSim353"
        metadata = {
            "language": lang,
            "score": score_percent,
            "type": con_type,
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


# load ws dataset
ws_dataset = load_dataset("0x22almostEvil/ws-semantics-simnrel", split="train")
print(ws_dataset)

# convert the dataset to a pandas dataframe & apply the create_qna function to each row of the dataframe to create QnA objects
qna_list = pd.DataFrame(ws_dataset).apply(qna_wrapper(), axis=1).tolist()

# export to parquet
qna_df = pd.DataFrame(qna_list, columns=["INSTRUCTION", "RESPONSE", "SOURCE", "METADATA"])
qna_df.to_parquet("semantics-ws-qna-oa.parquet", row_group_size=100, engine="pyarrow", index=False)
