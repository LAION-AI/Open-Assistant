from transformers import AutoTokenizer
from torch.utils.data import DataLoader
from rank_datasets import WebGPT, HFSummary, DataCollatorForPairRank


def test_hfsummary():
    
    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForPairRank(tokenizer, max_length=200)
    dataset = HFSummary()
    print(len(dataset))
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=8)
    for batch in dataloader:
        batch['input_ids'].shape
 

def test_webgpt():
    
    tokenizer = AutoTokenizer.from_pretrained("bigscience/mt0-large")
    collate_fn = DataCollatorForPairRank(tokenizer, max_length=200)
    dataset = WebGPT()
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=32)
    for batch in dataloader:
        print(batch['input_ids'].shape)


if __name__ == "__main__":
    test_hfsummary()
    # test_webgpt()