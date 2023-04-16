import json
import os
import re
import time

import pandas as pd
import requests
from tqdm import tqdm


def get_biostars_dataset(start_idx=9557161, accept_threshold=1000000, sleep=0.1, folder="biostars"):
    """
    Download BioStarts data set from the official API using GET requests

    Args:
        start_idx (int): The identifier (UID) of the post to retrieve; 9557161 was the last post included in the dataset
        accept_threshold (int): stop if this many posts with "has_accepted" true are retrieved
        sleep (float): Amount of time to sleep between requests
        folder (string): folder to store responses as JSON files
    Returns:
        Nothing. Content is saved to individual JSON files for each post.
    """

    headers = {"Content-Type": "application/json"}

    has_accepted_count = 0

    pbar = tqdm(range(start_idx, 0, -1), desc="Running ...")

    for idx in pbar:
        url = f"https://www.biostars.org/api/post/{idx}"
        file = os.path.join(folder, f"{idx}.json")

        if os.path.isfile(file):
            with open(file, "r") as f:
                data = json.load(f)

                if data.get("has_accepted"):
                    has_accepted_count += 1

            print(f"MSG: {file} exists. Skipping; Current accepted: {has_accepted_count}")
            continue

        r = requests.get(url, headers=headers)

        # print(r.status_code, r.reason)

        if r.status_code == 200:
            data = r.json()

            if data.get("has_accepted"):
                has_accepted_count += 1

            with open(file, "w") as f:
                json.dump(data, f)
            # print(f"MSG: File downloaded: {idx}; Current accepted: {has_accepted_count}")
        else:
            print("ERROR: Retrieving data: ", idx)
        time.sleep(sleep)

        if has_accepted_count == accept_threshold:
            print(f"{accept_threshold} entries with has_accepted found. Stopping.")
            break

        pbar.set_description(f"Item: {idx}; Accepted {has_accepted_count}")
        # tqdm.set_description(f"Cur: {idx}; Accepted: {has_accepted_count}")


def extract_accepted_data(folder="biostars", merged_json_file=None):
    """
    Extract questions paired with their accepted answers

    Args:
        folder (string): folder to store responses as JSON files
        merged_json_file (string): A JSON file with individual post content (from get_biostars_dataset()) merged as a JSON array of objects can be provided

    Returns:
        Nothing. Content is saved to the file: biostars_qa.parquet
    """

    # GET ALL ENTRIES ----
    # Merge individual files
    if merged_json_file is None:
        json_files = [file for file in os.listdir(folder) if file.endswith(".json")]

        all_entries = []

        for file in tqdm(json_files, desc="Get All Entries"):
            with open(os.path.join(folder, file), "r") as f:
                data = json.load(f)
                all_entries.append(data)

        with open(merged_json_file, "w") as f:
            json.dump(all_entries, f, indent=2)

    df = pd.read_json(merged_json_file)

    # GET QUESTIONS ----
    questions_df = df[(df["has_accepted"]) & (df["vote_count"] > 0) & (df["type"] == "Question")]

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


if __name__ == "__main__":
    get_biostars_dataset()
    extract_accepted_data()

    print("DONE")
