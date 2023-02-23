"""
    Open / close book QA datasets
"""
import glob
import json
import os
import re
from collections import OrderedDict
from urllib.request import urlopen

import numpy as np
from custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pair, format_rl_text
from datasets import load_dataset
from torch.utils.data import Dataset

# @agoryuno contributed this
re_reference_remove = re.compile(r"\[\d+(?:,\s*\d+)*?\]")


def index_squad_v2(example):
    if len(example["answers"]["text"]):
        answer = example["answers"]["text"][0]
    else:
        answer = "I do not have answer for that"
    return example["context"] + " " + example["question"], answer


def index_uasquad(example):
    if len(example["Answer"]):
        answer = example["Answer"]
    else:
        answer = "Я не маю на це відповіді"
    return example["Context"] + " " + example["Question"], answer


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


def index_wikihow(example):
    return example["title"] + ", explain step by step", example["result"]


def index_essay_instruction(example):
    return example["instructions"], example["titles"].strip() + "\n" + example["essays"]


def index_math_qa(example):
    """
    we are not including choices, so no need to output the "answer : <a,b,c,d>" part
    > if girls is 10 and boys is 20 , then 10 / 20 . so ratio of girls to boys is = 10 / 20 = 1 / 2 answer : a
    """
    return example["Problem"], example["Rationale"].split("answer : ", maxsplit=1)[0]


def index_eli5(example):
    return example["title"], example["answers"]["text"][0]


def index_gsm_hard(example):
    return example[
        "input"
    ] + "\nWrite a small snippet of python code to answer this", "Here's the code solution to the question\n```python\n{}\n```\n The answer should be {}".format(
        example["code"].strip(), example["target"]
    )


class QADataset(Dataset):
    """
    How to define a new QA dataset:

    Criteria : the qa dataset doesn't need fancy transform needed between fields rows or list

    1. Write the transform function, which maps each row into a pair of (question, answer) tuple

    2. Update DATASET_FORMAT_MAPPING with your dataset name and required parameter

        - index_fn : your transform function

        - name: the dataset name, this will be used when the name is different than huggingface load_dataset name

        - params: if your dataset require a predefined name, create a dictionary with the parameter name-value dictionary

    Feel free to create issues on GH for any suggestion how we can simplify this thing
    """

    DATASET_FORMAT_MAPPING = {
        "squad_v2": {"index_fn": index_squad_v2},
        "ua_squad": {
            "index_fn": index_uasquad,
            "name": "FIdo-AI/ua-squad",
            "params": {"field": "data"},
            "no_val": True,
        },
        "trivia_qa_nocontext": {
            "index_fn": index_trivia_qa_nocontext,
            "name": "trivia_qa",
            "params": {"name": "rc.nocontext"},
        },
        "trivia_qa_context": {"index_fn": index_trivia_qa_context, "name": "trivia_qa", "params": {"name": "rc"}},
        "adversarial_qa": {
            "index_fn": index_adversarial_qa,
            "params": {"name": "adversarialQA"},
        },
        "gsm8k_hard": {"index_fn": index_gsm_hard, "name": "reasoning-machines/gsm-hard", "no_val": True},
        "gsm8k": {"index_fn": index_gsm8k, "params": {"name": "main"}, "validation": "test"},
        "wikihow": {"name": "b-mc2/wikihow_lists", "index_fn": index_wikihow, "no_val": True},
        "essay_instruction": {
            "name": "ChristophSchuhmann/essays-with-instructions",
            "index_fn": index_essay_instruction,
            "no_val": True,
        },
        "math_qa": {
            "index_fn": index_math_qa,
        },
        "reddit_eli5": {"name": "eli5", "index_fn": index_eli5, "split_postfix": "_eli5"},
        "reddit_askh": {"name": "eli5", "index_fn": index_eli5, "split_postfix": "_askh"},
        "reddit_asks": {"name": "eli5", "index_fn": index_eli5, "split_postfix": "_asks"},
    }

    def __init__(self, dataset, cache_dir, split):
        self.no_val = False
        if dataset in self.DATASET_FORMAT_MAPPING:
            context = self.DATASET_FORMAT_MAPPING[dataset]
            if split == "validation" and "validation" in context:
                split = context["validation"]
            if "name" not in context:
                context["name"] = dataset
            if "split_postfix" in context:
                # append a postfix to split name, used in eli5 : test_eli5, test_asks, test_askh
                split += context["split_postfix"]
            if "params" not in context:
                context["params"] = {"cache_dir": cache_dir, "split": split}
            else:
                context["params"]["cache_dir"] = cache_dir
                context["params"]["split"] = split
            if "no_val" in context:
                self.no_val = True
            self.index_fn = context["index_fn"]
            self.dataset = load_dataset(context["name"], **context["params"])
        else:
            raise ValueError("Unknown dataset : " + dataset)
        self.length = len(self.dataset)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        data = self.dataset[idx]
        return format_pair(self.index_fn(data))


class WebGPT(Dataset):
    name = "webgpt"
    splits = OrderedDict(sft=0.25, reward_model=0.4, rl=0.35)  # fractions per task

    def __init__(self, split="sft") -> None:
        super().__init__()
        self.mode = split
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
        if self.mode == "sft":
            return format_pair((question, answer))
        elif self.mode == "rl":
            return format_rl_text((question, answer))


class SODA(Dataset):
    name = "soda"

    def process_soda_convo(self, data):
        pairs = []
        play_as = data["speakers"][1]
        question, answer = "", ""
        prefix, postfix = "", ""
        dialogue_bg = "{}{} {}{}".format(
            QA_SPECIAL_TOKENS["StartPrefix"],
            data["narrative"],
            "your are {}".format(play_as),
            QA_SPECIAL_TOKENS["EndPrefix"],
        )
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
                    [
                        "{}{}{}{}".format(QA_SPECIAL_TOKENS["Question"], p[0], QA_SPECIAL_TOKENS["Answer"], p[1])
                        for p in previous_chat
                    ]
                )
                if len(history):
                    history += "<sep>"
                prompt = QA_SPECIAL_TOKENS["Question"] + question + QA_SPECIAL_TOKENS["Answer"]
                pairs.append((dialogue_bg + history + prompt, answer))
                previous_chat.append((question, answer))

        return pairs

    def __init__(self, cache_dir, input_max_length=1024) -> None:
        super().__init__()

        self.pairs = []
        dataset = load_dataset("allenai/soda", cache_dir=cache_dir)["train"]
        for data in dataset:
            data_pair = self.process_soda_convo(data)
            for prompt, answer in data_pair:
                if len(prompt) < input_max_length:
                    self.pairs.append((prompt, answer))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        # special token added during preprocess
        return self.pairs[index]


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
        return format_pair(self.pairs[index])


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
                # DO NOT change this
                # its the data that had syntax error
                explanation = data["explaination"]
                self.pairs.append((joke, explanation))

        if len(question) > 0 and len(answer) > 0:
            self.pairs.append((question, answer))
        self.length = len(self.pairs)

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        return format_pair(self.pairs[index])


class TranslatedQA(Dataset):
    """
    Translation OA v3 results
    a list of non english translation of OA v3 instruction generated text in jsonl
    format for each line:
    {
        "text": "User: ... Assistant: ....",
        "meta": {"source": ... },
        "translate": [
            { "round": 1, "human":"...", "answer": "..."},
            ...
            { "round": K, "human":"...", "answer": "..."},
        ]
    }
    Since OA contain some code we needed to reference the original text to skip these
    """

    name = "oa_translated"

    def __init__(self, cache_dir) -> None:
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)
        path = os.path.join(cache_dir, self.name)
        os.makedirs(path, exist_ok=True)
        self.pairs = []
        for translated_jsonl in glob.glob(os.path.join(path, "*.jsonl")):
            with open(translated_jsonl, "r") as fin:
                for line in fin:
                    data = json.loads(line)
                    if "Python " in data["text"]:
                        # translation currently doesn't ignore code
                        # so we will have to reference original text
                        # for ignoring the translation
                        continue
                    prefix = ""
                    for convo_round in data["translate"]:
                        human, answer = format_pair((convo_round["human"], convo_round["answer"]))
                        if convo_round["round"] > 2:
                            self.pairs.append(("{}{}{}".format(prefix, "<sep>", human), answer))
                        else:
                            self.pairs.append((human, answer))

                        prefix += "{}{}{}{}".format(
                            QA_SPECIAL_TOKENS["Question"],
                            convo_round["human"],
                            QA_SPECIAL_TOKENS["Answer"],
                            convo_round["answer"],
                        )

        self.length = len(self.pairs)

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        return self.pairs[index]
