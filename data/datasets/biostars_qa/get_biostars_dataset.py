import json
import os
import time

import requests
from tqdm import tqdm

# There is a large number gap in post IDs the numbers skip from 9463943 to 494831
# Post ID: 9557161 was the last post included in the dataset
start_idx = 9557161
accept_threshold = 1000000
sleep = 0.1

headers = {"Content-Type": "application/json"}

has_accepted_count = 0

pbar = tqdm(range(start_idx, 0, -1), desc="Running ...")

for idx in pbar:
    url = f"https://www.biostars.org/api/post/{idx}"
    file = os.path.join("biostars", f"{idx}.json")

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
