import argparse
from collections import defaultdict

import numpy as np
import torch
from model_training.custom_datasets.rank_datasets import HellaSwagDataset, HFDataset, SHPDataset
from model_training.custom_datasets.ranking_collator import RankingDataCollator
from model_training.metrics import RewardMetrics
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers.trainer_utils import EvalPrediction
from utils import write_to_json

DATASETS = ["SHP", "Hellaswag", "HFdataset"]


def get_ranking_dataset(dataset, split):
    dataset = dataset.lower()
    if dataset == "shp":
        return SHPDataset(split=split)
    elif dataset == "hellaswag":
        return HellaSwagDataset(split=split)
    elif dataset == "hfdataset":
        return HFDataset(split=split)
    else:
        raise ValueError(f"Invalid dataset name, available {DATASETS}")


def batch_inference(inputs, model):
    batch, cu_lens = inputs
    batch = {k: v.to(model.device) for k, v in batch.items()}

    with torch.no_grad():
        logits = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]).logits.detach().cpu()

    if logits.dtype == torch.bfloat16:
        # As of Numpy 1.21.4, NumPy does not support bfloat16 (see
        # https://github.com/numpy/numpy/blob/a47ecdea856986cd60eabbd53265c2ca5916ad5d/doc/source/user/basics.types.rst ).
        # Until Numpy adds bfloat16, we must convert float32.
        logits = logits.to(torch.float32)
    logits = logits.numpy()

    labels = []
    for i, (s, e) in enumerate(zip(cu_lens[:-1], cu_lens[1:])):
        labels.extend([i] * (e - s))
    labels = np.array(labels).reshape(-1, 1)
    return EvalPrediction(predictions=logits.T, label_ids=labels.T)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--dataset", type=str, help="name of evaluation dataset")
    parser.add_argument("--split", type=str, help="dataset splits separated by comma", default="train")
    parser.add_argument("--model", type=str, help="Path or url of the model file")
    parser.add_argument("--metrics", type=str, help="metrics to evaluate", default="accuracy")
    parser.add_argument("--batch_size", type=int, help="Batch Size", default=8)
    parser.add_argument("--device", type=str, help="device", default="cuda")
    parser.add_argument("--dtype", type=str, help="data type", default=None)
    args = parser.parse_args().__dict__

    if args.get("device") != "cpu":
        device = torch.device(args.get("device")) if torch.cuda.is_available() else torch.device("cpu")
    else:
        device = torch.device("cpu")

    model_name = args.get("model")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, torch_dtype="auto" if not args.dtype else args.dtype
    )
    model.eval()
    model.to(device)
    max_length = args.get("max_length") or model.config.max_position_embeddings

    splits = args.get("split").split(",")
    dataset = get_ranking_dataset(args.get("dataset"), split=splits)
    collate_fn = RankingDataCollator(tokenizer)
    dataset = DataLoader(dataset, collate_fn=collate_fn, batch_size=args.get("batch_size"))

    metrics = args.get("metrics").split(",")
    compute_metrics = RewardMetrics(metrics)
    score_dict = defaultdict(float)
    for i, data in enumerate(tqdm(dataset)):
        eval_pred = batch_inference(data, model)
        results = compute_metrics(eval_pred)
        for metric in metrics:
            score_dict[metric] += results.get(metric)
    score_dict = {k: str(round(v / len(dataset), 3)) for k, v in score_dict.items()}

    results = {
        "model": model_name,
        "dataset": args.get("dataset"),
        "split": splits,
    }
    results.update(score_dict)

    print("RESULTS", results)
    write_to_json(f"rm-eval-{model_name.split('/')[-1]}-results.json", results)
