if __name__ == "__main__":
    from datasets import load_dataset

    dataset = load_dataset("michaelthwan/oa_wiki_qa_bart_10000row", split="train")
    print(dataset[0])
