from datasets import load_dataset

if __name__ == "__main__":
    ds = load_dataset("wannaphong/iapp_wiki_qa_squad_oa")
    print(ds)
