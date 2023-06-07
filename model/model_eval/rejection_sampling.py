import argparse

import model_training.models.reward_model  # noqa: F401 (registers reward model for AutoModel loading)
import numpy as np
import torch
from eval_datasets import RejectionSamplingDataset, SamplingDataCollator
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from utils import describe_samples, load_sampling_data, write_to_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--data_path", type=str, help="Path of the sampling data file")
    parser.add_argument("--model", type=str, help="Path or url of the model file")
    parser.add_argument("--rs", type=int, help="rejection sampling", default=3)
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
    max_length = args.get("max_length") or model.config.max_position_embeddings

    sr_report = load_sampling_data(args.get("data_path"))
    dataset = RejectionSamplingDataset(sr_report)
    collate_fn = SamplingDataCollator(tokenizer, max_length=max_length)
    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=1)

    RS = args.get("rs")
    selected_list, rejected_list = [], []
    for i, data in enumerate(dataloader):
        index = data.pop("sampling").detach().cpu().item()
        data = {k: v.to(device) for k, v in data.items()}
        pred = (
            model(**data)
            .logits[:, 0]
            .cpu()
            .detach()
            .numpy()
            .reshape(
                -1,
            )
        )
        sorted_indices = np.argsort(pred)
        prompt, replies, _ = dataset[index]
        selected_list.append(
            {
                "prompt": prompt,
                "outputs": [(replies[idx], str(round(pred[idx], 2))) for idx in reversed(sorted_indices[-RS:])],
            }
        )

        rejected_list.append(
            {"prompt": prompt, "outputs": [(replies[idx], str(round(pred[idx], 2))) for idx in sorted_indices[:-RS]]}
        )

    selected_stats = describe_samples(selected_list)
    rejected_stats = describe_samples(rejected_list)
    stats = {"rejected_samples": rejected_stats, "selected_samples": selected_stats}
    write_to_json("selected_samples", selected_list)
    write_to_json("rejected_samples", rejected_list)
    write_to_json("comparison", stats)
