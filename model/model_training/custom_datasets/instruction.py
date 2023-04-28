"""
    These are in the form of 'INSTRUCTION', 'RESPONSE'
"""
from datasets import load_dataset
from model_training.custom_datasets.formatting import DatasetEntry
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
}


class InstructionDataset(Dataset):
    def __init__(self, dataset, cache_dir, split, max_words=512, mode="sft"):
        assert mode in ("sft", "rl")
        self.name = dataset
        self.dataset = load_dataset(INSTRUCTION_DATASETS[dataset], cache_dir=cache_dir, split=split)
        self.instruction_column = "INSTRUCTION" if dataset != "minimath" else "question"
        self.response_column = "RESPONSE" if dataset != "minimath" else "answer"
        self.max_words = max_words

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> DatasetEntry:
        data = self.dataset[idx]
        lang = None
        # these datasets have been found to have above 95% english sentences.
        if self.name in ["grade_school_math_instructions"]:
            lang = "en"
        return DatasetEntry(questions=[data[self.instruction_column]], answers=[data[self.response_column]], lang=lang)
