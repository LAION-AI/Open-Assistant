import io
import json
import math
import os
import pickle
import random
import re
import sys
import urllib
import zipfile
from typing import List

import requests
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_ids(raw_file: str, video_id_pattern: str) -> List[str]:
    video_ids = []
    overlap = ""
    with open(raw_file, "r") as f:
        while True:
            chunk = f.read(100000)  # arbitrary chunk size
            if not chunk:
                break
            chunk = overlap + chunk
            match = re.findall(video_id_pattern, chunk)
            if match:
                for vid in match:
                    video_ids.append(vid.strip("'\""))
            overlap = chunk[-10:]  # in case video_id is split between chunks
    return list(set(video_ids))  # dedup


def get_title(video_id):
    params = {"format": "json", "url": f"https://www.youtube.com/watch?v={video_id}"}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string
    try:
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            title = data["title"]
    except urllib.request.HTTPError:
        title = None
    return title


def generate_instruction(title: str) -> str:
    # TODO: Ask a generative LM, "Can you rephrase the title of {title} into a request form?"
    title = title.lower()
    if "how to" in title:
        return "Please explain " + title[title.index("how to") :]


def get_subs(video_id, languages=["en"]):
    try:
        subs_dump = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        subs = ""
        for utterence in subs_dump:
            subs += utterence["text"] + " "
        # TODO: add punctuation
    except urllib.request.HTTPError:
        subs = None
    return subs


def main(output_dir: str = "data"):
    """Download and prepare the dataset for use."""
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists("./temp/raw_caption.json"):
        print("Downloading HowTo100M raw_caption.zip...")
        print(" might take some time(3.4G)...")
        url = "https://www.rocq.inria.fr/cluster-willow/amiech/howto100m/raw_caption.zip"
        response = requests.get(url)
        zipped = zipfile.ZipFile(io.BytesIO(response.content))
        zipped.extractall("./temp")

    if not os.path.exists("./temp/video_ids.pkl"):
        print("Retrieving video ids...")
        filename = "./temp/raw_caption.json"
        video_id_pattern = '"[0-9A-Za-z_-]{11}"'
        video_ids = get_video_ids(filename, video_id_pattern)
        with open("./temp/video_ids.pkl", "wb") as f:
            pickle.dump(video_ids, f)
    else:
        with open("./temp/video_ids.pkl", "rb") as f:
            video_ids = pickle.load(f)

    print("Extracting instruction-response pairs...")
    dataset = []
    for video_id in tqdm(video_ids):
        title = get_title(video_id)
        if title is None:  # video is not available any more
            continue
        else:
            instruction = generate_instruction(title)
            if instruction:
                response = get_subs(video_id)
                dataset.append({"instruction": instruction, "response": response, "source": "YouTube"})
    print(f"Total {len(dataset)} pairs extracted.")

    print("Splitting and saving data...")
    random.shuffle(dataset)
    train_limit = math.ceil(len(dataset) * 0.6)  # TODO: parameterize ratios
    dev_limit = math.ceil(len(dataset) * 0.8)
    train, validation, test = (
        dataset[:train_limit],
        dataset[train_limit:dev_limit],
        dataset[dev_limit:],
    )
    splits = {"train": train, "validation": validation, "test": test}
    for split in ["train", "validation", "test"]:
        with open(f"{output_dir}/youtube_subs_howto100M_{split}.jsonl", "w") as f:
            for datapoint in splits[split]:
                f.write(f"{json.dumps(datapoint)}\n")
    print("All Done!")


if __name__ == "__main__":
    sys.exit(main())
