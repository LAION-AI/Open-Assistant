"""
This script should help to detect any keywords or other unwanted appearances in the datasets
RUN WITH:
python check_dataset_appearances.py -d <datasets> --cache_dir <path-to-cache-dir> --mode <one of sft, rm, rl>

e.g.:
python check_dataset_appearances.py -d gpt4all webgpt --cache_dir .cache --mode sft

python check_dataset_appearances.py -d alpaca_gpt4 vicuna gpteacher_roleplay red_pajama wizardlm_70k --cache_dir .cache --mode sft
python check_dataset_appearances.py -d wizardlm_70k --cache_dir .cache --mode sft

python check_dataset_appearances.py -d alpaca_gpt4 vicuna gpteacher_roleplay wizardlm_70k joke poem_instructions oa_stackexchange tell_a_joke --cache_dir .cache --mode sft
python check_dataset_appearances.py joke  --cache_dir .cache --mode sft

python check_dataset_appearances.py -d webgpt gpt4all code_alpaca minimath humaneval_mbpp_codegen_qa humaneval_mbpp_testgen_qa grade_school_math_instructions recipes cmu_wiki_qa oa_wiki_qa_bart_10000row prosocial_dialogue explain_prosocial soda oa_leet10k dolly15k --cache_dir .cache --mode sft
python check_dataset_appearances.py -d soda oa_leet10k dolly15k --cache_dir .cache --mode sft
"""
import argparse
import pprint
from collections import defaultdict

from model_training.check_dataset_counts import Mode
from model_training.custom_datasets import get_one_dataset
from model_training.custom_datasets.formatting import DatasetEntrySft, PretrainDatasetEntry

# from model_training.custom_datasets.qa_datasets import (
#     re_reference_remove,
#     re_single_reference_remove,
#     re_whitespace_newline_match,
# )
# from model_training.custom_datasets.utils import FILTER_BY_WORDS

RE_TO_CHECK = []  # [re_whitespace_newline_match, re_reference_remove, re_single_reference_remove]
# STRINGS_TO_CHECK = [*FILTER_BY_WORDS]
STRINGS_TO_CHECK = [
    "as a language model",
    "as an AI language model",
    "As a large language model",
    "As an AI ",
    "an AI language model you don't have",
    "As an AI language model, I cannot",
    "As an AI language model, I do not",
    "As an AI language model, I am not able",
    "As an AI language model, I don't have personal",
    "I am an AI language model and do not",
    "As an AI language model, I don't have",
    "As an AI language model, I am only able",
    "AI language model and I do not",
    "As an AI language model, I cannot modify",
    "As an AI language model, I do not",
    "I know as an AI language model you don't have",
    "as an AI language model, you cannot",
    "I'm sorry, but as an AI language model",
    "As an AI language model, I don't have",
    "I'm an AI ",
    "I am an AI ",
    "my name is OpenAI",
    "trained by OpenAI",
    "as an OpenAI language model",
    "As your dedicated AI language model",
    "As a hypothetical AI",
    "As a neutral AI",
    "my knowledge cutoff",
    "my knowledge cut off",
    "As a machine",
    "I cannot assist",
    "I do not have personal preferences",
    "I don't have personal preferences",
    "Unfortunately, I cannot provide",
    "I'm sorry, I cannot",
    "I'm sorry, I cannot generate",
    "AI cannot create or program",
    "I'm afraid I cannot create",
]


def argument_parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--datasets",
        nargs="+",
        required=True,
        help="""
        Multiple datasets can be passed to set different options.
        For example, run as:

           ./check_dataset_counts.py --datasets math oasst_export_eu

        to check the counts of the math and the oasst_export_eu dataset.
    """,
    )
    parser.add_argument("--mode", dest="mode", type=Mode, choices=list(Mode))
    parser.add_argument("--cache_dir", dest="cache_dir", type=str)

    args, _ = parser.parse_known_args()

    return args


def check_in_dataset_row(row: str | list[str] | tuple[str], matched=dict[str, list]):
    def _check_single_string(row: str, matched: dict[str, list]) -> dict[str, list]:
        for exp in RE_TO_CHECK:
            if exp.match(row) is not None:
                matched[exp].append(row)
        for string in STRINGS_TO_CHECK:
            if string.lower() in row.lower():
                string_idx = row.lower().index(string.lower())
                matched[string].append(row[max(string_idx - 50, 0) : string_idx + 50])
        return matched

    if isinstance(row, str):
        matched = _check_single_string(row, matched)
    elif isinstance(row, (list, tuple)):
        for r in row:
            if not isinstance(r, str):
                raise ValueError(f"Unexpected type: {type(row)}")
            matched = _check_single_string(r, matched)
    elif isinstance(row, DatasetEntrySft):
        formatted = row.get_formatted(eos_token="</s>")
        for r in formatted:
            if not isinstance(r, str):
                raise ValueError(f"Unexpected type: {type(r)}")
            matched = _check_single_string(
                r.replace("<|assistant|>", "").replace("<|prompter|>", "").replace("</s>", ""), matched
            )
    elif isinstance(row, PretrainDatasetEntry):
        matched = _check_single_string(row.text, matched)
    else:
        raise ValueError(f"Received unexpected type: {type(row)}.")
    return matched


def iterate_over_dataset(ds):
    matched = defaultdict(list)
    for row in ds:
        check_in_dataset_row(row, matched)
    return matched


if __name__ == "__main__":
    args = argument_parsing()
    pp = pprint.PrettyPrinter(indent=4)

    overview_dct = {}
    train_datasets, val_datasets = {}, {}
    for dataset_name in args.datasets:
        train, val = get_one_dataset(None, dataset_name, mode=args.mode.value, data_path=args.cache_dir)
        train_datasets[dataset_name] = train
        if val is not None:
            val_datasets[dataset_name] = val
        matched_train = iterate_over_dataset(train)
        matched_val = iterate_over_dataset(val)
        train_dct = {k: len(v) for k, v in matched_train.items()}
        val_dct = {k: len(v) for k, v in matched_val.items()}
        unified_keys = list(set(train_dct.keys()).union(set(val_dct.keys())))
        unified_counts = {k: train_dct.get(k, 0) + val_dct.get(k, 0) for k in unified_keys}
        import pdb

        pdb.set_trace()
        if len(unified_counts):
            overview_dct[dataset_name] = unified_counts
            print(f"\nFOUND THE FOLLOWING APPEARANCES FOR DATASET {dataset_name}:")
            pp.pprint(unified_counts)
        # if len(matched_train) != 0:
        #     pp.pprint(f"Found the following occurances in TRAIN {dataset_name}:")
        #     pp.pprint(dict(matched_train))
        # if len(matched_val) != 0:
        #     pp.pprint(f"Found the following occurances in VAL {dataset_name}:")
        #     pp.pprint(dict(matched_val))
        if len(matched_train) + len(matched_val) == 0:
            print(f"\nNOT FIND OF THE SPECIFIED REGULAR EXPRESSIONS OR FILTER WORDS. FOR THE DATASET {dataset_name}")
    if len(overview_dct) > 0:
        pp.pprint(overview_dct)
