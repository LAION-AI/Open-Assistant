from datasets import concatenate_datasets, load_dataset


def load(languages: list = ["en", "de", "fr", "es", "it", "pt", "nl", "hu"]):
    ds = None
    for lang in languages:
        if ds is None:
            ds = load_dataset(f"sedthh/gutenberg_{lang}")
        else:
            ds = concatenate_datasets([ds, f"sedthh/gutenberg_{lang}"])
    return ds


if __name__ == "__main__":
    ds = load()
    print(ds["train"])
