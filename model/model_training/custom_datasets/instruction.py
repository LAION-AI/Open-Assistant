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
    "humaneval_mbpp_codegen_qa": "OllieStanley/humaneval-mbpp-codegen-qa",
    # Write unit tests to do task X
    "humaneval_mbpp_testgen_qa": "OllieStanley/humaneval-mbpp-testgen-qa",
    "grade_school_math_instructions": "qwedsacf/grade-school-math-instructions",
    "recipes": "dctanner/oa_recipes",
    "ubuntu_dialogue_qa": "sedthh/ubuntu_dialogue_qa",
    "cmu_wiki_qa": "sedthh/cmu_wiki_qa",
    "youtube_subs_howto100m": "totuta/youtube_subs_howto100M",
    "iapp_wiki_qa_squad": "wannaphong/iapp_wiki_qa_squad_oa",
    "zhihu-kol": "wangrui6/zhihu-kol",
    "minimath": "kentsui/minimath",
    "oa_wiki_qa_bart_10000row": "michaelthwan/oa_wiki_qa_bart_10000row",
    "oa_leet10k": "ehartford/oa_leet10k",
    "poem_instructions": "checkai/instruction-poems",
    "oa_stackexchange": "donfu/oa-stackexchange",
    "tell_a_joke": "mikegarts/oa_tell_a_joke_20000",
    "wizardlm_70k": "ehartford/WizardLM_alpaca_evol_instruct_70k_unfiltered",
    "megacode": "rombodawg/MegaCodeTraining112k",
    "evol_instruct_code": "nickrosh/Evol-Instruct-Code-80k-v1",
    "evol-codealpaca-v1": "theblackcat102/evol-codealpaca-v1",
    "cot_submix_original": "conceptofmind/cot_submix_original",
}


class InstructionDataset(Dataset):
    def __init__(self, dataset, cache_dir, split, mode="sft", fill_min_length: Optional[int] = None, seed: int = 42):
        assert mode in ("sft", "rl")
        self.name = dataset
        self.mode = mode
        data_files = None
        if dataset == "minimath":
            self.instruction_column = "question"
            self.response_column = "answer"
        elif dataset in ("wizardlm_70k", "evol_instruct_code", "evol-codealpaca-v1"):
            self.instruction_column = "instruction"
            self.response_column = "output"
        elif dataset == "cot_submix_original":
            self.instruction_column = "inputs"
            self.response_column = "targets"
        elif dataset == "megacode":
            self.instruction_column = "prompt"
            self.response_column = "completion"
            data_files = "RombosCodeTraining112k.json"
        else:
            self.instruction_column = "INSTRUCTION"
            self.response_column = "RESPONSE"

        num_invalid = 0

        ds = load_dataset(INSTRUCTION_DATASETS[dataset], cache_dir=cache_dir, split=split, data_files=data_files)
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
            print(f"[Warning] {num_invalid} entries of {dataset} were invalid.")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> DatasetEntry:
        questions, answers = self.dataset[idx]

        lang: str | None = None
        # use "en" for datasets which have more than 95% English messages
        if self.name in [
            "humaneval_mbpp_codegen_qa",
            "humaneval_mbpp_testgen_qa",
            "grade_school_math_instructions",
            "recipes",
            "poem_instructions",
            "tell_a_joke",
        ]:
            lang = "en"

        return create_dataset_entry_qa(
            mode=self.mode,
            questions=questions,
            answers=answers,
            lang=lang,
        )
