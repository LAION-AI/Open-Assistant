from collections import defaultdict

from model_training.custom_datasets.formatting import DatasetEntryLm, DatasetEntrySft


def check_in_dataset_row(
    row: str | list[str] | tuple[str],
    matched: dict[str, list],
    strings_to_match: list[str] = [],
    regex_strings_to_match: list[str] = [],
):
    def _check_single_string(row: str, matched: dict[str, list]) -> dict[str, list]:
        for exp in regex_strings_to_match:
            if exp.match(row) is not None:
                matched[exp].append(row)
        for string in strings_to_match:
            if string.lower() in row.lower():
                matched[string].append(row)
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
    elif isinstance(row, DatasetEntryLm):
        matched = _check_single_string(row.text, matched)
    else:
        raise ValueError(f"Received unexpected type: {type(row)}.")
    return matched


def iterate_over_dataset(ds, strings_to_match, regex_strings_to_match):
    matched = defaultdict(list)
    for row in ds:
        check_in_dataset_row(row, matched, strings_to_match, regex_strings_to_match)
    if len(matched) == 0:
        for string in strings_to_match:
            matched[string] = []
        for regex in regex_strings_to_match:
            matched[regex] = []
    return matched
