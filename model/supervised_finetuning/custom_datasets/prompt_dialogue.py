import os
from urllib.request import urlopen

from torch.utils.data import Dataset


class PromptGeneratedDataset(Dataset):
    """Generates from flan 11B
    User: What are the best methods for preventing a slave trade?

    Rosey: The best methods ....
    <|endoftext|>

    we are ignoring results with multiple lines for now
    """

    url = "https://github.com/Rallio67/language-model-agents/raw/main/chat_dialogue_v2_c.txt"

    def __init__(self) -> None:
        super().__init__()
        os.makedirs("datasets", exist_ok=True)
        chat_dialogue = os.path.join("datasets", "chat_dialogue_v2_c.txt")
        if not os.path.exists(chat_dialogue):
            with urlopen(self.url) as file:
                content = file.read().decode()
            with open(chat_dialogue, "w") as fout:
                fout.write(content)

        question = ""
        answer = ""
        self.pairs = []
        with open(chat_dialogue, "r") as f:

            for line in f:
                try:
                    line = line.rstrip()
                    if len(line) == 0:
                        continue
                    elif line == "<|endoftext|>" and len(question) > 0 and len(answer) > 0:
                        self.pairs.append((question, answer))
                        question = ""
                        answer = ""
                    elif line[:4] == "User":
                        question = line.split(":", maxsplit=1)[1]
                    elif line == "Rosey:":
                        question = ""
                        answer = ""
                    elif len(line) > 4:  # should be bot answer
                        answer = line.split(":", maxsplit=1)[1]
                except IndexError:
                    question = ""
                    answer = ""

        if len(question) > 0 and len(answer) > 0:
            self.pairs.append((question, answer))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        question, answer = self.pairs[index]
        return question, answer


if __name__ == "__main__":
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer

    from .dialogue_collator import DialogueDataCollator

    tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-2B-multi")
    tokenizer.add_special_tokens({"pad_token": "<|endoftext|>", "sep_token": "<|endoftext|>"})
    dataset = PromptGeneratedDataset()
    collate_fn = DialogueDataCollator(tokenizer, padding=True, max_length=128)
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=5)
    for batch in dataloader:
        print(batch["input_ids"].shape)
