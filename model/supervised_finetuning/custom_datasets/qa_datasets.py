"""
    Open / close book QA datasets
"""
import json
import os
import re
from urllib.request import urlopen

import numpy as np
from datasets import load_dataset
from torch.utils.data import Dataset

# @agoryuno contributed this
re_reference_remove = re.compile(r"\[\d+(?:,\s*\d+)*?\]")

QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


def index_squad_v2(example):
    if len(example["answers"]["text"]):
        answer = example["answers"]["text"][0]
    else:
        answer = "I do not have answer for that"
    return example["context"] + " " + example["question"], answer


def index_trivia_qa_nocontext(example):
    # dummy return one randomly
    return example["question"], example["answer"]["aliases"][np.random.randint(len(example["answer"]["aliases"]))]


def index_trivia_qa_context(example):
    question = example["question"]
    if len(example["search_results"]["search_context"]):
        context = example["search_results"]["search_context"][
            np.random.randint(len(example["search_results"]["search_context"]))
        ]
    else:
        context = ""
    answer = example["answer"]["aliases"][np.random.randint(len(example["answer"]["aliases"]))]

    return context + " " + question, answer


def index_adversarial_qa(example):
    return example["title"] + ". " + example["context"] + " " + example["question"], example["answers"]["text"][0]


def index_gsm8k(example):
    return example["question"], example["answer"]


class QADataset(Dataset):
    def __init__(self, dataset, cache_dir, split):
        if dataset == "squad_v2":
            self.index_fn = index_squad_v2
            self.dataset = load_dataset("squad_v2", cache_dir=cache_dir, split=split)
        elif dataset == "trivia_qa_nocontext":
            self.index_fn = index_trivia_qa_nocontext
            self.dataset = load_dataset("trivia_qa", "rc.nocontext", split=split, cache_dir=cache_dir)
        elif dataset == "trivia_qa_context":
            self.index_fn = index_trivia_qa_context
            self.dataset = load_dataset("trivia_qa", "rc", split=split, cache_dir=cache_dir)
        elif dataset == "adversarial_qa":
            self.index_fn = index_adversarial_qa
            self.dataset = load_dataset("adversarial_qa", "adversarialQA", split=split, cache_dir=cache_dir)
        elif dataset == "gsm8k":
            self.index_fn = index_gsm8k
            self.dataset = load_dataset("gsm8k", "main", split=split, cache_dir=cache_dir)
        elif dataset == "adversarial_qa":
            self.index_fn = index_adversarial_qa
            self.dataset = load_dataset("adversarial_qa", "adversarialQA", split=split, cache_dir=cache_dir)
        else:
            raise ValueError("Unknown dataset : " + dataset)

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        data = self.dataset[idx]
        return self.index_fn(data)


class WebGPT(Dataset):

    name = "webgpt"

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
            questions[question] = re_reference_remove.sub(
                "", row["answer_0" if row["score_0"] > row["score_1"] else "answer_1"]
            )

        self.questions = questions

    def __len__(self):
        return len(self.index2question)

    def __getitem__(self, index):
        question = self.index2question[index]
        answer = self.questions[question]
        return [question, answer]


class SODA(Dataset):

    name = "soda"

    def process_soda_convo(self, data):
        pairs = []
        play_as = data["speakers"][1]
        prefix = "{}{}. {}{}".format(
            QA_SPECIAL_TOKENS["StartPrefix"],
            data["narrative"],
            "your name {}".format(play_as),
            QA_SPECIAL_TOKENS["EndPrefix"],
        )
        question, answer = "", ""
        prefix, postfix = "", ""
        previous_chat = []

        for idx, convo in enumerate(data["dialogue"]):
            if idx % 2 == 0:
                question = convo
                prefix = data["speakers"][idx]
            else:
                answer = convo
                postfix = data["speakers"][idx]
            if len(question) and len(answer) and prefix != postfix and postfix == play_as:
                history = "<sep>".join(
                    ["{}{}{}".format(p[0], QA_SPECIAL_TOKENS["Answer"], p[1]) for p in previous_chat]
                )
                if len(history):
                    history += "<sep>"
                pairs.append((prefix + history + question, answer))
                previous_chat.append((question, answer))
        return pairs

    def __init__(self, cache_dir, max_sample_size=10000, input_max_length=1024) -> None:
        super().__init__()

        self.pairs = []
        dataset = load_dataset("allenai/soda", cache_dir=cache_dir)["train"]
        for data in dataset:
            data_pair = self.process_soda_convo(data)
            for (prompt, answer) in data_pair:
                if len(prompt) < input_max_length:
                    self.pairs.append((prompt, answer))

            if len(self.pairs) > max_sample_size:
                break

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        question, answer = self.pairs[index]
        return question, answer


class SODADialogue(Dataset):
    url = "https://drive.google.com/uc?id=1TOGQfr419n8wpzJpYLLw4nB3tSKD8zXV"

    def __init__(self, cache_dir, verbose=True):

        path = os.path.join(cache_dir, "soda_dialog.jsonl")

        if not os.path.exists(path):
            import gzip
            import shutil

            import gdown

            gdown.download(self.url, output=os.path.join(cache_dir, "soda_dialog.jsonl.gz"))

            with gzip.open(os.path.join(cache_dir, "soda_dialog.jsonl.gz"), "rb") as f_in:
                with open(path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

        self.pairs = []
        faulty = 0
        with open(path) as fin:
            for line in fin:
                conversation = json.loads(line)
                question_answer_pairs = ()

                question_answers = conversation["text"].split("User: ")
                for question_answer in question_answers[1:]:  # first element is empty
                    try:
                        question, answer = question_answer.split("\nAssistant: ")
                        question_answer_pairs += (
                            question,
                            answer,
                        )
                    except ValueError:
                        # there might be some extra 'User: ' or 'Assistant: ' tokens in the dataset that cause trouble..
                        faulty += 1
                        continue

                self.pairs.append(question_answer_pairs)

        if verbose:
            print("For SODA dialogue dataset found {} faults within the total {} dialogs".format(faulty, len(self)))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        return self.pairs[index]


class JokeExplaination(Dataset):

    name = "joke"
    url = "https://gist.github.com/theblackcat102/42b697e24a13fdb499e20edfbf618361/raw/1834dca207898c15f93b809d1195f6f6e47c9e1e/joke_explained.jsonl"

    def __init__(self, cache_dir) -> None:
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)
        joke_explain_filename = os.path.join(cache_dir, "joke_explaination.jsonl")
        if not os.path.exists(joke_explain_filename):
            with urlopen(self.url) as file:
                content = file.read().decode()
            with open(joke_explain_filename, "w") as fout:
                fout.write(content)

        question = ""
        answer = ""
        self.pairs = []
        with open(joke_explain_filename, "r") as f:
            for line in f:
                data = json.loads(line)
                joke = data["joke"]
                explanation = data["explaination"]
                self.pairs.append((joke, explanation))

        if len(question) > 0 and len(answer) > 0:
            self.pairs.append((question, answer))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        question, answer = self.pairs[index]
        return question, answer


# https://huggingface.co/datasets/aquamuse
