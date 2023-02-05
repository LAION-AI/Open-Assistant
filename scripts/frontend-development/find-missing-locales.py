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
            not_translated.extend(get_not_translated(en_json[key], translation_json[key], key))
    return not_translated


def get_missing(en_json, translation_json):
    return [key for key in en_json.keys() if key not in translation_json]


def print_result(missing, not_translated, file):
    if len(missing):
        print("[{0}] - missing: {1} {2}".format(path.basename(path.dirname(file)), path.basename(file), missing))
    if len(not_translated):
        print(
            "[{0}] - potentially untranslated: {1} {2}".format(
                path.basename(path.dirname(file)), path.basename(file), not_translated
            )
        )


def audit(file, en_file):
    en_json = load(open(en_file))
    translation_json = load(open(file))
    print_result(get_missing(en_json, translation_json), get_not_translated(en_json, translation_json), file)


def main():
    for en_file in glob(path.join(DIR, EN_PATH)):
        for file in glob(path.join(DIR, ALL_PATH)):
            if path.basename(en_file) == path.basename(file) and file != en_file:
                audit(file, en_file)


if __name__ == "__main__":
    main()
