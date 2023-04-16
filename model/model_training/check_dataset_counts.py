import argparse
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from model_training.utils.utils import _strtobool, get_dataset


class Mode(Enum):
    sft = "sft"
    rm = "rm"
    rl = "rl"

    def config_name(self) -> str:
        match self:
            case Mode.sft:
                return "config.yaml"
            case Mode.rm:
                return "config_rm.yaml"
            case Mode.rl:
                return "config_rl.yaml"

    def default_config(self) -> str:
        match self:
            case Mode.sft:
                return "defaults"
            case Mode.rm:
                return "defaults_rm"
            case Mode.rl:
                return "defaults_rlhf"


def read_yaml(dir: str | Path, config_file: str) -> dict[str, Any]:
    with open(Path(dir) / config_file, "r") as f:
        return yaml.safe_load(f)


def argument_parsing(notebook=False, notebook_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
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
    parser.add_argument("--output_path", dest="output_path", default="dataset_counts.csv")

    if notebook:
        args, remaining = parser.parse_known_args(notebook_args)
    else:
        args, remaining = parser.parse_known_args()

    # Config from YAML
    mode: Mode = args.mode
    configs = read_yaml("./configs", config_file=mode.config_name())
    conf = configs[mode.default_config()]
    if "all" in args.datasets:
        conf["datasets"] = configs[mode.default_config()]["datasets"] + configs[mode.default_config()]["datasets_extra"]
    else:
        # reset datasets, so that we only get the datasets defined in configs and remove the ones in the default
        datasets_list = list()

        for name in args.datasets:
            # check and process multiple datasets
            if "," in name:
                for n in name.split(","):
                    datasets_value = configs[n].get("datasets") or configs[n]["datasets_extra"]
            # check if dataset is extra key in config
            elif name in configs:
                datasets_value = configs[name].get("datasets") or configs[name]["datasets_extra"]
            # check in default config
            elif name in configs[mode.default_config()]["datasets"]:
                datasets_value = [name]
            else:
                raise ValueError(
                    f'Error: Could not find the dataset "{name}" in {mode.config_name()}. ',
                    f"Tried to look for this dataset within th key {mode.default_config()} ",
                    "and as seperate key.",
                )

            datasets_list.extend(datasets_value)
    conf["mode"] = mode
    conf["output_path"] = args.output_path
    conf["datasets_extra"] = []
    conf["datasets"] = datasets_list
    # Override config from command-line
    parser = argparse.ArgumentParser()
    for key, value in conf.items():
        type_ = type(value) if value is not None else str
        if type_ == bool:
            type_ = _strtobool
        parser.add_argument(f"--{key}", type=type_, default=value)
        # Allow --no-{key}  to remove it completely
        parser.add_argument(f"--no-{key}", dest=key, action="store_const", const=None)

    args = parser.parse_args(remaining)
    print(args)
    return args


if __name__ == "__main__":
    args = argument_parsing()

    train, evals = get_dataset(args, mode=args.mode)
    overview_df = pd.DataFrame(columns=["dataset_name", "train_counts", "eval_counts", "total_counts"])
    for idx, dataset_name in enumerate(args.datasets):
        eval_count = len(evals.get(dataset_name, []))
        overview_df.loc[idx] = [
            dataset_name,
            len(train.datasets[idx]),
            eval_count,
            len(train.datasets[idx]) + eval_count,
        ]
    print(overview_df)
    overview_df.to_csv(args.output_path, index=False)
