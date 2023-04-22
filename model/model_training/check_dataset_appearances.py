"""
This script should help to detect any keywords or other unwanted appearances in the datasets
RUN WITH:
python check_dataset_appearances.py -d <datasets> --cache_dir <path-to-cache-dir> --mode <one of sft, rm, rl>

e.g.:
python check_dataset_appearances.py -d gpt4all webgpt --cache_dir .cache --mode sft
"""
import argparse
import pprint
from collections import defaultdict

from model_training.custom_datasets import get_one_dataset
from model_training.custom_datasets.entities import Mode
from model_training.custom_datasets.formatting import DatasetEntry
from model_training.custom_datasets.qa_datasets import (
    re_reference_remove,
    re_single_reference_remove,
    re_whitespace_newline_match,
)
from model_training.custom_datasets.utils import FILTER_BY_WORDS

RE_TO_CHECK = [re_whitespace_newline_match, re_reference_remove, re_single_reference_remove]
STRINGS_TO_CHECK = [*FILTER_BY_WORDS]


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
            if string in row:
                string_idx = row.index(string)
                matched[string].append(row[max(string_idx - 50, 0) : string_idx + 50])
        return matched

    if isinstance(row, str):
        matched = _check_single_string(row, matched)
    elif isinstance(row, (list, tuple)):
        for r in row:
            if not isinstance(r, str):
                raise ValueError(f"Unexpected type: {type(row)}")
            matched = _check_single_string(r, matched)
    elif isinstance(row, DatasetEntry):
        formatted = row.get_formatted(mode=args.mode, eos_token="</s>")
        for r in formatted:
            if not isinstance(r, str):
                raise ValueError(f"Unexpected type: {type(r)}")
            matched = _check_single_string(
                r.replace("<|assistant|>", "").replace("<|prompter|>", "").replace("</s>", ""), matched
            )
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

    train_datasets, val_datasets = {}, {}
    for dataset_name in args.datasets:
        print(f"start with dataset {dataset_name}")
        train, val = get_one_dataset(None, dataset_name, mode=args.mode.value, data_path=args.cache_dir)
        train_datasets[dataset_name] = train
        if val is not None:
            val_datasets[dataset_name] = val
        matched_train = iterate_over_dataset(train)
        matched_val = iterate_over_dataset(val)
        if len(matched_train) != 0:
            pp.pprint(f"Found the following occurances in TRAIN {dataset_name}:")
            pp.pprint(dict(matched_train))
        if len(matched_val) != 0:
            pp.pprint(f"Found the following occurances in VAL {dataset_name}:")
            pp.pprint(dict(matched_val))
        if len(matched_train) + len(matched_val) == 0:
            print("Did not find of the specified regular expressions or filter words.")
