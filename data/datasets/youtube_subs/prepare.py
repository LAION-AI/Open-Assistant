import os
import sys
import json
import math
import random
import re
from typing import List

from youtube_transcript_api import YouTubeTranscriptApi


def get_video_ids(raw_file: str, video_id_pattern: str) -> List[str]:
    video_ids = []
    overlap = ""
    with open(raw_file, 'r') as f:
        while True:
            chunk = f.read(100000) # arbitrary chunk size
            if not chunk: break
            chunk += overlap
            match = re.findall(video_id_pattern, chunk)
            if match:
                for vid in match:
                    video_ids.append(vid.strip("'\""))
            overlap = chunk[-10:] # in case video_id is split between chunks
    return set(video_ids) # dedup


def get_title(video_id, languages=['en']):
    raise NotImplementedError


def generate_instruction(title: str) -> str:
    raise NotImplementedError


def get_subs(video_id, languages=['en']):
    return YouTubeTranscriptApi.get_transcript(video_id, languages=languages)


def main(output_dir: str = "data"):
    """Download and prepare the dataset for use."""
    os.makedirs(output_dir, exist_ok=True)

    print("Downloading HowTo100M raw_caption.zip...")
    url="https://www.rocq.inria.fr/cluster-willow/amiech/howto100m/raw_caption.zip"

    # TODO: download and unzip it

    filename="raw_caption.json"
    video_id_pattern = '"[0-9A-Za-z_-]{11}"'
    video_ids = get_video_ids(filename, video_id_pattern)

    # TODO: get title and make a "instruction" of asking for how-to
    # TODO: get_subtitles and organize them into a long string as a "response"
    # TODO: organize as instruction, response, source as YouTube
    dataset = []
    for video_id in video_ids:
        title = get_title(video_id)
        instruction = generate_instruction(title)
        response = get_subs(video_id)
        dataset.append({'instruction': instruction,
                        'response': response,
                        'source': 'YouTube'})
    # random.shuffle(dataset)
    train_limit = math.ceil(len(dataset) * 0.6) # TODO: parameterize ratios
    dev_limit = math.ceil(len(dataset) * 0.8)
    train, validation, test = (
        dataset[:train_limit],
        dataset[train_limit:dev_limit],
        dataset[dev_limit:],
    )
    splits = {"train": train, "validation": validation, "test": test}
    for split in ["train", "validation", "test"]:
        with open(f"{output_dir}/youtube_subs_{split}.jsonl", "w") as f:
            for datapoint in splits[split]:
                f.write(f"{json.dumps(datapoint)}\n")


if __name__ == "__main__":
    sys.exit(main())