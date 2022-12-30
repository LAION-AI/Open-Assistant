from transformers import AutoTokenizer
from torch.utils.data import DataLoader
from rank_datasets import WebGPT, HFSummary, CollateFN


def test_hfsummary():
    
    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = CollateFN(tokenizer)
    dataset = HFSummary()
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=8)
    for batch in dataloader:
        print(batch[0]['input_ids'].shape)
 

def test_webgpt():
    
    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = CollateFN(tokenizer)
    dataset = WebGPT()
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=32)
    for batch in dataloader:
        print(batch[0]['input_ids'].shape)


if __name__ == "__main__":
    test_hfsummary()
    # test_webgpt()