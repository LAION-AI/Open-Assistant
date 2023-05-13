"""
    These are in the form of 'INSTRUCTION', 'RESPONSE'
"""
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
}


class InstructionDataset(Dataset):
    def __init__(self, dataset, cache_dir, split, mode="sft"):
        assert mode in ("sft", "rl")
        self.name = dataset
        self.mode = mode
        if dataset == "minimath":
            self.instruction_column = "question"
            self.response_column = "answer"
        elif dataset == "wizardlm_70k":
            self.instruction_column = "instruction"
            self.response_column = "output"
        else:
            self.instruction_column = "INSTRUCTION"
            self.response_column = "RESPONSE"

        ds = load_dataset(INSTRUCTION_DATASETS[dataset], cache_dir=cache_dir, split=split)
        self.dataset = []
        num_invalid = 0
        for i in range(len(ds)):
            data = ds[i]
            if (
                data[self.instruction_column] is not None
                and len(data[self.instruction_column].strip()) > 0
                and data[self.response_column] is not None
                and len(data[self.response_column].strip()) > 0
                and _filter_by_words(data[self.instruction_column])
                and _filter_by_words(data[self.response_column])
            ):
                self.dataset.append(data)
            else:
                num_invalid += 1
        if num_invalid > 0:
            print(f"[Warning] {num_invalid} entries of {dataset} were invalid.")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> DatasetEntry:
        data = self.dataset[idx]
        lang = None
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
            questions=[data[self.instruction_column]],
            answers=[data[self.response_column]],
            lang=lang,
        )
