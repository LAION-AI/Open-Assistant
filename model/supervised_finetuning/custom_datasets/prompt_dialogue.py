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
        question, answer = self.pairs[index]
        return question, answer
