from datasets import load_dataset

if __name__ == "__main__":
    ds = load_dataset("pythainlp/tlcv2.0_oa")
    print(ds)
