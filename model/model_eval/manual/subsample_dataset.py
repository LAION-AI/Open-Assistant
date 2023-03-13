import argparse
import gzip
import json
import random
from pathlib import Path

import pydantic
from oasst_data import ExportMessageTree


def load_messega_trees(input_file_path: str | Path, lang_codes: list[str]) -> list[ExportMessageTree]:
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)

    if input_file_path.suffix == ".gz":
        file_in = gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
    else:
        file_in = input_file_path.open("r", encoding="UTF-8")

    trees = []

    with file_in:
        # read one message tree per line
        for line in file_in:
            dict_tree = json.loads(line)

            # validate data
            tree: ExportMessageTree = pydantic.parse_obj_as(ExportMessageTree, dict_tree)

            if tree.prompt.lang not in lang_codes or tree.tree_state != "ready_for_export":
                continue

            trees.append(tree)

    return trees


def write_file(output_file_path: str | Path, items: list) -> None:
    if not isinstance(output_file_path, Path):
        output_file_path = Path(output_file_path)

    if output_file_path.suffix == ".gz":
        file_out = gzip.open(str(output_file_path), "wt", encoding="UTF-8")
    else:
        file_out = open(output_file_path, "wt", encoding="UTF-8")

    with file_out:
        for obj in items:
            x = obj
            if isinstance(x, pydantic.BaseModel):
                x = obj.dict(exclude_none=True)
            json.dump(x, file_out)
            file_out.write("\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-file",
        type=str,
        help="Name of oasst exprt file to read",
    )

    parser.add_argument(
        "--output-file",
        type=str,
        default="out.jsonl",
        help="Output file name",
    )

    parser.add_argument("-k", type=int, default=100, help="Number of trees to sample")

    parser.add_argument(
        "--lang",
        type=str,
        default="en",
        help="List of comma separated language codes",
    )

    parser.add_argument("--only-prompts", action="store_true", default=False)

    parser.add_argument("--only-text", action="store_true", default=False)

    parser.add_argument(
        "--seed",
        type=int,
        default="42",
        help="rng seed",
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    lang_codes = args.lang.split(",")
    random.seed(args.seed)
    trees = load_messega_trees(args.input_file, lang_codes)
    sub_sample = random.sample(trees, k=args.k)

    if args.only_prompts:
        sub_sample = [x.prompt for x in sub_sample]

        if args.only_text:
            sub_sample = [x.text for x in sub_sample]

    write_file(args.output_file, sub_sample)


if __name__ == "__main__":
    main()
