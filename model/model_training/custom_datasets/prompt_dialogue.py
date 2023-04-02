import gzip
import json
import re
from pathlib import Path
from typing import Optional

import requests
from datasets import load_dataset
from model_training.custom_datasets.oasst_dataset import ListDataset
from torch import Generator, randperm
from torch.utils.data import Dataset, random_split


def load_oig_file(
    source_url: str,
    val_split: float = 0.2,
    cache_dir: str = ".cache/",
    no_cache: bool = False,
    max_count: Optional[int] = None,
    min_length: Optional[int] = 1000,
    manual_seed: int = 287631038922,
) -> tuple[ListDataset, ListDataset]:
    generator = Generator()
    generator.manual_seed(manual_seed)

    file_name = source_url[source_url.rindex("/") + 1 :]

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    local_path = cache_dir / file_name

    # download file if not cached
    if not local_path.exists() or local_path.stat().st_size == 0 or no_cache:
        print(f"downloading {source_url} to {local_path}")
        r = requests.get(source_url, stream=True)
        with local_path.open(mode="wb") as fd:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                fd.write(chunk)

    # read the file
    if local_path.suffix == ".gz":
        file_in = gzip.open(str(local_path), mode="tr", encoding="UTF-8")
    else:
        file_in = local_path.open("r", encoding="UTF-8")

    with file_in:
        # read one message tree per line
        conversations = []
        for line in file_in:
            data = json.loads(line)

            text = data.get("text")
            if not text:
                continue

            fragments = re.split(r"\s*(\<(?:human|bot)\>)\:\s*", text)

            role = None
            turns = []
            s = ""
            for x in fragments:
                if x == "<human>" or x == "<bot>":
                    if role != x:
                        if role is not None:
                            turns.append(s)
                            s = ""
                        role = x
                    continue
                s += x.strip()
            turns.append(s)
            if role == "<bot>" and len(turns) % 2 == 0:
                conversations.append(turns)

    # shuffling with torch generator (not modifying python's standard random state)
    random_order = randperm(len(conversations), generator=generator).tolist()
    conversations = [conversations[i] for i in random_order]

    # concatenate multiple QA pairs until total length is above min_length
    if min_length is not None:
        merged_conversations = []
        merge = []
        for x in conversations:
            if sum(len(s) for s in merge) >= min_length:
                merged_conversations.append(merge)
                merge = []
            merge += x
        merged_conversations.append(merge)
        conversations = merged_conversations

    # if max count was specified select a random subset
    if max_count is not None:
        conversations = conversations[:max_count]

    avg_turn_count = sum(len(x) for x in conversations) / len(conversations)
    splits = random_split(conversations, lengths=[1.0 - val_split, val_split], generator=generator)

    train = ListDataset(splits[0])
    val = ListDataset(splits[1])

    print(f"OIG data {str(local_path)}: {len(train)=}, {len(val)=} ({avg_turn_count=:.1f})")

    return train, val


class Gpt4All(Dataset):
    def __init__(self, mode: str, cache_dir: str = None) -> None:
        super().__init__()
        self.mode = mode
        dataset = load_dataset(
            "Nebulous/gpt4all_pruned",
            data_files="data_pruned_3.jsonl",
            cache_dir=cache_dir,
        )
        self.rows = [(row["prompt"], row["response"]) for row in dataset["train"]]

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        question, answer = self.rows[index]
        if self.mode == "sft":
            return (question, answer)
        elif self.mode == "rl":
            return (question,)
