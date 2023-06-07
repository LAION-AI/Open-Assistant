from datasets import load_dataset

if __name__ == "__main__":
    ds = load_dataset("zirui3/TSSB-3M-instructions")
    print(ds)
