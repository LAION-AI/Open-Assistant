import json
import os
import re

import pandas as pd
from tqdm import tqdm

folder_path = "biostars"

json_files = [file for file in os.listdir(folder_path) if file.endswith(".json")]

# GET ALL ENTRIES ----
all_entries = []

for file in tqdm(json_files, desc="Get All Entries"):
    with open(os.path.join(folder_path, file), "r") as f:
        data = json.load(f)
        all_entries.append(data)

with open("all_entries.json", "w") as f:
    json.dump(all_entries, f, indent=2)

df = pd.read_json("all_entries.json")

# GET QUESTIONS ----
questions_df = df[(df["has_accepted"]) & (df["vote_count"] > 0) & (df["type"] == "Question")]
question_uids = questions_df["uid"].tolist()

# GET ANSWERS ----
answers_df = df[(df["has_accepted"]) & (df["vote_count"] > 0) & (df["type"] == "Answer")]

# GET MATCHED QUESTIONS/ANSWERS ----
matched_uids = []

for input_str in tqdm(answers_df["url"], desc="Find Matched Answers"):
    # extract the question and answer IDs using regular expressions
    match_obj = re.match(r"https://www.biostars.org/p/(\d+)/#(\d+)", input_str)
    question_id = match_obj.group(1)
    answer_id = match_obj.group(2)

    # create a dictionary with the question and answer IDs and add it to the output list
    output_dict = {"question": question_id, "answer": answer_id}
    matched_uids.append(output_dict)

# GET MATCHED QUESTIONS/ANSWERS ----
matched_qa = []

for match in tqdm(matched_uids, desc="Get Matched Answers"):
    entry = {}

    # match = {'question': '477589', 'answer': '477883'}

    entry_obj = questions_df[questions_df["uid"] == int(match["question"])]
    if entry_obj.empty:
        continue
    entry_dict = entry_obj.iloc[0].to_dict()

    entry["INSTRUCTION"] = entry_dict["content"]
    entry["SOURCE"] = "biostars"
    entry[
        "METADATA"
    ] = f'{{"uid": {entry_dict["uid"]}, "view_count": {entry_dict["view_count"]}, "vote_count": {entry_dict["vote_count"]}}}'

    entry_obj = answers_df[answers_df["uid"] == int(match["answer"])]
    entry_dict = entry_obj.iloc[0].to_dict()
    entry["RESPONSE"] = entry_dict["content"]

    # sorted_entry = dict(sorted(entry.items(), key=lambda x: x[0] != "INSTRUCTION"))
    sorted_entry = {k: entry[k] for k in ["INSTRUCTION", "RESPONSE", "SOURCE", "METADATA"]}
    matched_qa.append(sorted_entry)

with open("matched_biostars_qa.json", "w") as f:
    json.dump(matched_qa, f, indent=2)

len(matched_qa)

# Read filtered JSON and convert to parquet format
tmp = pd.read_json("matched_biostars_qa.json")  # or any other way
tmp.to_parquet("biostars_qa.parquet", row_group_size=100, engine="pyarrow")
