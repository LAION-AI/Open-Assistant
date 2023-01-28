import json
import os
from urllib.request import urlopen

from custom_datasets.formatting import format_pair
from torch.utils.data import Dataset


class PromptGeneratedDataset(Dataset):
    """Generates from flan 11B
    User: What are the best methods for preventing a slave trade?

    Rosey: The best methods ....
    <|endoftext|>

    we are ignoring results with multiple lines for now
    """

    name = "prompt_dialogue"
    url = "https://github.com/Rallio67/language-model-agents/raw/main/chat_dialogue_v2_c.txt"

    def __init__(self, cache_dir) -> None:
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)
        chat_dialogue = os.path.join(cache_dir, "chat_dialogue_v2_c.txt")
        if not os.path.exists(chat_dialogue):
            with urlopen(self.url) as file:
                content = file.read().decode()
            with open(chat_dialogue, "w") as fout:
                fout.write(content)

        question = ""
        answer = ""
        self.pairs = []
        with open(chat_dialogue, "r") as f:
            corpus = f.read().split("<|endoftext|>")
            for dialogue in corpus:
                dialogue = dialogue.strip()
                if "Rosey:" in dialogue:
                    user, bot = dialogue.split("Rosey:", maxsplit=1)
                    question = user.split(":", maxsplit=1)[1].strip()
                    answer = bot.strip()
                    if len(answer) and len(question):
                        self.pairs.append((question, answer))

        if len(question) > 0 and len(answer) > 0:
            self.pairs.append((question, answer))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        return format_pair(self.pairs[index])


class InstructionTuning(Dataset):
    """
    We have seen some promising capabilities from instruction tuning
    with the following mix of datasets that are derived from datasets
    available online.
    The files for this data are in json format as a list of tuples
    where each tuple is (source,instruction_response_pair)

        - instruction_tuning_dataset_alpha_part1.json
        - instruction_tuning_dataset_alpha_part2.json

    Not to be confused with unatural instruction
    """

    name = "instruction_dataset"
    url_part_2 = (
        "https://github.com/Rallio67/language-model-agents/raw/main/instruction_tuning_dataset_alpha_part2.json"
    )
    url_part_1 = (
        "https://github.com/Rallio67/language-model-agents/raw/main/instruction_tuning_dataset_alpha_part1.json"
    )

    def __init__(self, cache_dir) -> None:
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)

        self.pairs = []
        for file_link in [self.url_part_1, self.url_part_2]:
            basename = file_link.split("/")[-1]
            instruction_tune_file = os.path.join(cache_dir, basename)
            if not os.path.exists(instruction_tune_file):
                with urlopen(file_link) as file:
                    content = file.read().decode()
                with open(instruction_tune_file, "w", encoding="utf-8") as fout:
                    fout.write(content)

            with open(instruction_tune_file, "r", encoding="utf-8") as f:
                datasets = json.load(f)
                for row in datasets:
                    _, response_pair = row
                    question, answer = response_pair.split("\n\n", maxsplit=1)
                    answer = answer.replace("<|endoftext|>", "").strip()
                    self.pairs.append((question, answer))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        return format_pair(self.pairs[index])
