import gzip
import json
import re
from pathlib import Path
from typing import List, Mapping, Optional, Sequence, Union

import requests
from datasets import load_dataset
from model_training.custom_datasets.formatting import DatasetEntrySft, Role, Utterance
from model_training.custom_datasets.oasst_dataset import ListDataset
from model_training.custom_datasets.utils import _filter_by_words
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
            data_files="data_singleround_pruned_3.jsonl",
            cache_dir=cache_dir,
        )
        self.rows = [
            [row["prompt"], row["response"]]
            for row in dataset["train"]
            if _filter_by_words(row["prompt"]) and _filter_by_words(row["response"])
        ]

        dataset_multi = load_dataset(
            "Nebulous/gpt4all_pruned",
            data_files="data_multiround_pruned_3.jsonl",
            cache_dir=cache_dir,
        )
        for row in dataset_multi["train"]["conversation"]:
            if (processed_conversation := self.process_conversation(row)) is not None:
                self.rows.append(processed_conversation)

    @staticmethod
    def process_conversation(conv: list[dict[str, None | str]]) -> list[str] | None:
        dialogue = []
        role = None
        messages = []
        # drop conversations that start with Bot
        if conv[0]["Bot"] is not None:
            return None
        for line in conv:
            if line["User"] and line["Bot"]:
                raise ValueError("Unexpected dataformat. Should receive only User or Bot data, not both.")
            if (message := line["User"]) is not None:
                speaker = "Human"
            elif (message := line["Bot"]) is not None:
                speaker = "Assistant"
            else:
                continue
            if _filter_by_words(message) is None:
                return None
            if role != speaker:
                if role is not None:
                    dialogue.append("\n".join(messages))
                    messages = []
                role = speaker
            messages.append(message.strip())

        if role is not None and len(messages) > 0:
            dialogue.append("\n".join(messages))
        return dialogue

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index: int) -> list[str] | tuple[str]:
        dialogue: list = self.rows[index]
        if self.mode == "sft":
            return dialogue
        elif self.mode == "rl":
            return tuple(dialogue[:-1])


class OrcaChat(Dataset):
    name = "orca-chat"

    def __init__(self, data_files: Union[List[str], str] = "orca-chat-gpt4.json", cache_dir: str = None) -> None:
        self.dataset = load_dataset("shahules786/orca-chat", split="train", data_files=data_files, cache_dir=cache_dir)

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        conversation, instruction = [self.dataset[idx][key] for key in ("conversation", "instruction")]
        conversation = [(item["input"], item["output"]) for item in conversation]
        conversation = list(sum(conversation, ()))
        conv_utt: list[Utterance] = [
            (
                Utterance(
                    text=conv,
                    role=Role.prompter if i % 2 == 0 else Role.assistant,
                )
            )
            for i, conv in enumerate(conversation)
        ]

        return DatasetEntrySft(conversation=conv_utt, system_message=instruction)


class DolphinMix(Dataset):
    name = "dophin-mix"

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        num_samples: Optional[int] = None,
        max_char_len: int = 8000,
        seed: int = 42,
        data_files: Union[
            str, Sequence[str], Mapping[str, Union[str, Sequence[str]]]
        ] = "flan5m-alpaca-uncensored.jsonl",
        split: str = "train",
    ):
        # flan5m-alpaca-uncensored.jsonl has total entries 2840090
        self.dataset = load_dataset("ehartford/dolphin", data_files=data_files, cache_dir=cache_dir)
        self.dataset = self.dataset[split].shuffle(seed).flatten_indices()
        if num_samples:
            self.dataset = self.dataset.select(range(num_samples))
        self.max_char_len = max_char_len
        instructions = sorted(set([item["instruction"] for item in self.dataset]))

        self.conversations = []
        for inst in instructions:
            data_sample = self.dataset.filter(lambda example: example["instruction"] == inst)
            conversation_len = len(inst)
            conversation = []
            for entry in data_sample:
                input, output = entry["input"], entry["output"]
                conversation.append({"input": input, "output": output})
                conversation_len += len(input) + len(output)
                if conversation_len >= self.max_char_len:
                    self.conversations.append({"conversation": conversation, "instruction": inst})
                    conversation_len = len(inst)
                    conversation = []

            if len(conversation) > 0:
                self.conversations.append({"conversation": conversation, "instruction": inst})

    def __len__(self) -> int:
        return len(self.conversations)

    def __getitem__(self, idx) -> DatasetEntrySft:
        conversation, instruction = [self.conversations[idx][key] for key in ("conversation", "instruction")]
        conversation = [(item["input"], item["output"]) for item in conversation]
        conversation = list(sum(conversation, ()))
        conv_utt: list[Utterance] = [
            (
                Utterance(
                    text=conv,
                    role=Role.prompter if i % 2 == 0 else Role.assistant,
                )
            )
            for i, conv in enumerate(conversation)
        ]

        return DatasetEntrySft(conversation=conv_utt, system_message=instruction)
