from datasets import load_dataset

if __name__ == "__main__":
    ds = load_dataset("iapp_wiki_qa_squad")
    print(ds["train"])
