from datasets import load_dataset

if __name__ == "__main__":
    ds = load_dataset("thaisum")
    print(ds["train"])
