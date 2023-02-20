from collections import defaultdict
from glob import glob
from json import load
from os import path

ALL_PATH = "../../website/public/locales/**/*.json"
DIR = path.dirname(__file__)
EN_PATH = "../../website/public/locales/en/*.json"


def get_not_translated(en_json, translation_json, parent_key=None):
    not_translated = []
    for key in en_json.keys():
        if key in translation_json and translation_json[key] == en_json[key]:
            not_translated.append(("{0}.{1}".format(parent_key, key) if parent_key else key))
        elif isinstance(en_json[key], dict):
            if key not in translation_json:
                msg = f"{parent_key}.{key} (and children)" if parent_key else "{key} (and children)"
                not_translated.append(msg)
            else:
                not_translated.extend(get_not_translated(en_json[key], translation_json[key], key))
    return not_translated


def get_missing(en_json, translation_json):
    return [key for key in en_json.keys() if key not in translation_json]


def print_result(missing, not_translated, file):
    if len(missing):
        print("[{0}] - {1}\tmissing: {2}".format(path.basename(path.dirname(file)), path.basename(file), missing))
    if len(not_translated):
        print(
            "[{0}] - {1}\tpotentially untranslated: {2}".format(
                path.basename(path.dirname(file)), path.basename(file), not_translated
            )
        )


def audit(file, en_file):
    en_json = load(open(en_file))
    translation_json = load(open(file))
    return (get_missing(en_json, translation_json), get_not_translated(en_json, translation_json), file)


def main():
    per_language_dict = defaultdict(list)
    for en_file in glob(path.join(DIR, EN_PATH)):
        for file in glob(path.join(DIR, ALL_PATH)):
            if path.basename(en_file) == path.basename(file) and file != en_file:
                file_info = audit(file, en_file)
                lang = path.basename(path.dirname(file))
                per_language_dict[lang].append(file_info)
    for results in per_language_dict.values():
        list(map(lambda args: print_result(*args), results))
        print()


if __name__ == "__main__":
    main()
