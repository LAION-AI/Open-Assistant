"""
    These are in the form of 'INSTRUCTION', 'RESPONSE'
"""
import random
from typing import Optional

from datasets import load_dataset
from model_training.custom_datasets.formatting import DatasetEntry, create_dataset_entry_qa
from model_training.custom_datasets.utils import _filter_by_words
from torch.utils.data import Dataset

INSTRUCTION_DATASETS = {
    # Note humaneval_mbpp_codegen_qa returns a code string that we would want to at least wrap in ``` marks`
    "humaneval_mbpp_codegen_qa": {"dataset_path": "OllieStanley/humaneval-mbpp-codegen-qa", "lang": "en"},
    # Write unit tests to do task X
    "humaneval_mbpp_testgen_qa": {"dataset_path": "OllieStanley/humaneval-mbpp-testgen-qa", "lang": "en"},
    "grade_school_math_instructions": {"dataset_path": "qwedsacf/grade-school-math-instructions", "lang": "en"},
    "recipes": {"dataset_path": "dctanner/oa_recipes", "lang": "en"},
    "ubuntu_dialogue_qa": {"dataset_path": "sedthh/ubuntu_dialogue_qa"},
    "cmu_wiki_qa": {"dataset_path": "sedthh/cmu_wiki_qa"},
    "youtube_subs_howto100m": {"dataset_path": "totuta/youtube_subs_howto100M"},
    "iapp_wiki_qa_squad": {"dataset_path": "wannaphong/iapp_wiki_qa_squad_oa"},
    "zhihu-kol": {"dataset_path": "wangrui6/zhihu-kol"},
    "minimath": {
        "dataset_path": "kentsui/minimath",
        "instruction_column": "question",
        "response_column": "answer",
    },
    "oa_wiki_qa_bart_10000row": {"dataset_path": "michaelthwan/oa_wiki_qa_bart_10000row"},
    "oa_leet10k": {"dataset_path": "ehartford/oa_leet10k"},
    "poem_instructions": {"dataset_path": "checkai/instruction-poems", "lang": "en"},
    "oa_stackexchange": {"dataset_path": "donfu/oa-stackexchange"},
    "tell_a_joke": {"dataset_path": "mikegarts/oa_tell_a_joke_20000", "lang": "en"},
    "wizardlm_70k": {
        "dataset_path": "ehartford/WizardLM_alpaca_evol_instruct_70k_unfiltered",
        "instruction_column": "instruction",
        "response_column": "output",
    },
    "megacode": {
        "dataset_path": "rombodawg/MegaCodeTraining112k",
        "instruction_column": "prompt",
        "response_column": "completion",
        "data_files": "RombosCodeTraining112k.json",
    },
    "megacode2": {
        "dataset_path": "rombodawg/LosslessMegaCodeTrainingV2_1m_Evol_Uncensored",
        "instruction_column": "USER",
        "response_column": "ASSISTANT",
        "data_files": "DeDuped_LosslessMegaCodeTrainingV2_942k_Evol_Uncensored.json",
    },
    "megacode3": {
        "dataset_path": "rombodawg/LosslessMegaCodeTrainingV3_2.2m_Evol",
        "instruction_column": "USER",
        "response_column": "ASSISTANT",
        "data_files": "LosslessMegaCodeTrainingV3_2.2m_Evol.json",
    },
    "evol_instruct_code": {
        "dataset_path": "nickrosh/Evol-Instruct-Code-80k-v1",
        "instruction_column": "instruction",
        "response_column": "output",
    },
    "evol-codealpaca-v1": {
        "dataset_path": "theblackcat102/evol-codealpaca-v1",
        "instruction_column": "instruction",
        "response_column": "output",
    },
    "cot_submix_original": {
        "dataset_path": "conceptofmind/cot_submix_original",
        "instruction_column": "inputs",
        "response_column": "targets",
    },
}


class InstructionDataset(Dataset):
    def __init__(
        self,
        name: str,
        dataset_path: str,
        cache_dir: str,
        split: str,
        mode: str = "sft",
        instruction_column: str = "INSTRUCTION",
        response_column: str = "RESPONSE",
        data_files: Optional[str] = None,
        lang: Optional[str] = None,
        fill_min_length: Optional[int] = None,
        seed: int = 42,
    ):
        assert mode in ("sft", "rl")
        self.name = name
        self.mode = mode

        self.instruction_column = instruction_column
        self.response_column = response_column
        self.data_files = data_files
        self.lang = lang

        num_invalid = 0

        ds = load_dataset(dataset_path, cache_dir=cache_dir, split=split, data_files=data_files)
        self.dataset: list[tuple[list[str], list[str]]] = []

        questions, answers = [], []
        item_len = 0

        rng = random.Random(seed)
        order = list(range(len(ds)))
        rng.shuffle(order)

        # filter entries and optionally combine multiple entries
        for i in order:
            entry = ds[i]
            q = entry[self.instruction_column]
            a = entry[self.response_column]
            if (
                q is not None
                and len(q.strip()) > 0
                and a is not None
                and len(a.strip()) > 0
                and _filter_by_words(q)
                and _filter_by_words(a)
            ):
                questions.append(q)
                answers.append(a)
                item_len += len(a) + len(q)

                if fill_min_length is None or fill_min_length < item_len:
                    self.dataset.append((questions, answers))
                    item_len = 0
                    questions, answers = [], []
            else:
                num_invalid += 1

        if len(questions) > 0 and len(answers) > 0:
            self.dataset.append((questions, answers))

        if num_invalid > 0:
            print(f"[Warning] {num_invalid} entries of {name} ({dataset_path}) were invalid.")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> DatasetEntry:
        questions, answers = self.dataset[idx]

        return create_dataset_entry_qa(
            mode=self.mode,
            questions=questions,
            answers=answers,
            lang=self.lang,
        )


RAG_DATASETS = {
    "multi-chapter-summaries": "shahules786/Multi-chapter-summaries",
}


class RAGDataset(Dataset):
    def __init__(
        self,
        dataset,
        split: str = "train",
        cache_dir: str = ".cache/",
    ):
        if dataset not in RAG_DATASETS.keys():
            raise ValueError(f"Invalid dataset {dataset}")

        if dataset == "multi-chapter-summaries":
            self.prompt, self.context, self.response = "prompt", "context", "summary"

        self.dataset = load_dataset(RAG_DATASETS[dataset], cache_dir=cache_dir)[split]

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        prompt, context, response = [self.dataset[idx][key] for key in [self.prompt, self.context, self.response]]

        return create_dataset_entry_qa(mode="sft", questions=[prompt + context], answers=[response])
