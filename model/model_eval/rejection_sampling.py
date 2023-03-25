import argparse
import torch
from utils import load_sampling_data
from eval_datasets import RejectionSamplingDataset
from model_training.custom_datasets.ranking_collator import RankingDataCollator



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--data_path", type=str, help="Path of the sampling data file")
    parser.add_argument("--model", type=str, help="Path or url of the model file")
    parser.add_argument("--max_length", type=int, help="max length of input")
    parser.add_argument("--device", type=str, help="device", default="cpu")
    args = parser.parse_args().__dict__


    if args.get("device") != "cpu":
        device = torch.device(args.get("device")) if torch.cuda.is_available() else torch.device("cpu")
    else:
        device = torch.device("cpu")

    model_name = args.get("model")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    model.to(device)
    max_length = args.get("max_length")

    sr_report = load_sampling_data(args.get("data_path"))
    dataset = RejectionSamplingDataset(sr_report)
    collate_fn = RankingDataCollator(tokenizer)
    dataloader = DataLoader(dataset,collate_fn=collate_fn,batch_size=1)

    ##TODO
    ## Inference 
    ## Rejection sampling
    ## Writing results to seperate files

