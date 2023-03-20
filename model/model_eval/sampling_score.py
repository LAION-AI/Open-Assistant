import argparse
import os
import json
from dataset import get_dataloader
import torch
import numpy as np
import pandas as pd
from model.model_training.utils import get_tokenizer
from model.model_training.models.reward_model import RewardModel

def load_sampling_data(path):
    """
    Load sampling data and ensure appropriate keys are present.
    """

    if os.path.exists(path):
        data = json.load(open(path))
    else:
        raise FileNotFoundError(f"Sampling data {path} not found")

    if "prompts" not in data.keys():
        raise KeyError("sampling data should contain prompts key")

    keys = set(data["prompts"][0].keys())
    required_keys = set(["prompt", "results"])
    keys = keys.intersection(required_keys)
    if keys != required_keys:
        raise KeyError(f"Missing keys {required_keys - keys} ")

    return data


def batch_inference(model, dataloader):
    """
    Batch inference
    """

    scores, sampling = [], []
    for i, data in enumerate(dataloader):
        sampling.append(data.pop("sampling").cpu().detach().numpy())
        data = {k: v.squeeze() for k, v in data.items()}
        pred = model(**data).logits[:, 0].cpu().detach().numpy()
        scores.append(pred)

    return np.hstack(sampling), np.hstack(scores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--data_path", type=str, help="Path of the sampling data file")
    parser.add_argument("--model", type=str, help="Path or url of the model file")
    parser.add_argument("--batch_size", type=int, help="device", default=4)
    parser.add_argument("--device", type=str, help="device", default="cpu")
    parser.add_argument(
        "--save", type=bool, help="whether to save the results", default=True
    )

    args = parser.parse_args().__dict__
    if args.get("device") != "cpu":
        device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
    else:
        device = torch.device("cpu")

    data = load_sampling_data(args.get("data_path"))

    reward_name = args.get("model")
    
    ##TODO
    rank_model = RewardModel().from_pretrained(model)
    tokenizer = get_tokenizer(model)
    rank_model.eval()
    rank_model.to(device)
    max_len = model.max_len

    dataloader = get_dataloader(data, tokenizer, max_len, args.get("batch_size"), device)
    sampling, scores = batch_inference(rank_model, dataloader)
    
    df = pd.DataFrame({"sampling": sampling, "score": scores})
    id2label = {v: k for k, v in dataloader.dataset.label2id.items()}
    df["sampling"] = df["sampling"].map(id2label)
    results = df.groupby("sampling")["score"].mean().to_dict()
    results["mean_reward"] = df["score"].mean().astype('str')
    print("RESULTS: ", results)


    results = {"model_name":data["model_name"], "results":results, "reward_model":args.get("model")}
    results = {"model_name":data["model_name"], "results":results}
    name = "-".join(data["model_name"].split("/"))
