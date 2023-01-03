from datasets import load_dataset
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, Subset


class SquadV2Dataset(Dataset):
    def __init__(self, cache_dir, split):
        self.dataset = load_dataset("squad_v2", cache_dir=cache_dir, split=split)

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        data = self.dataset[idx]
        # dummy return first answer
        return "".join([data["title"], ". ", data["context"], " " + data["question"]]), data["answers"]["text"][0]


class WebGPT(Dataset):
    def __init__(self) -> None:
        super().__init__()

        dataset = load_dataset("openai/webgpt_comparisons")
        questions = {}
        # using prompt as our index will allows us
        # to add additional generated prompt later
        self.index2question = {}
        for row in dataset["train"]:
            question = row["question"]["full_text"]
            if question not in self.index2question:
                self.index2question[len(self.index2question)] = question

            # only keep the best answer
            questions[question] = row["answer_0" if row["score_0"] > row["score_1"] else "answer_1"]

        self.questions = questions

    def __len__(self):
        return len(self.index2question)

    def __getitem__(self, index):
        question = self.index2question[index]
        answer = self.questions[question]
        return [question, answer]


def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def get_one_dataset(conf, dataset_name):
    dataset_name = dataset_name.lower()

    if dataset_name == "squadv2":
        raise ValueError("SquadV2 is not diverse enough for generation .. ")
        train = SquadV2Dataset(conf.cache_dir, "train")
        eval = SquadV2Dataset(conf.cache_dir, "validation")
    elif dataset_name == "webgpt":
        dataset = WebGPT()
        train, eval = train_val_dataset(dataset, val_split=0.2)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")

    return train, eval
