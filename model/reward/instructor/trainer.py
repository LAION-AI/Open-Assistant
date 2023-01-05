import os
from argparse import ArgumentParser
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import evaluate
import numpy as np
import torch

from torch import nn
from torch.utils.data import ConcatDataset
from transformers import Trainer

try:
    from .rank_datasets import DataCollatorForPairRank, HFSummary, WebGPT
    from .utils import (
        argument_parsing, 
        get_tokenizer, 
        train_val_dataset,
        load_model)
except ImportError:
    from rank_datasets import DataCollatorForPairRank, HFSummary, WebGPT
    from utils import (
        argument_parsing, 
        get_tokenizer, 
        train_val_dataset,
        load_model)

os.environ["WANDB_PROJECT"] = "reward-model"

accuracy = evaluate.load("accuracy")
PARSER = ArgumentParser()
PARSER.add_argument("config", type=str)


def compute_metrics(eval_pred):
    predictions, _ = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=[0] * predictions.shape[0])


class RankLoss(nn.Module):
    def __init__(self, eps=1e-8) -> None:
        super().__init__()
        self.eps = eps
        self.log_sigmoid = nn.LogSigmoid()

    def forward(self, pos, neg):
        return -self.log_sigmoid(pos - neg + self.eps).mean()


class RankTrainer(Trainer):
    def __init__(self, 
            loss_function: Optional[Literal["rank"]] = None, 
            *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loss_fct = nn.CrossEntropyLoss()
        self.loss_function = None
        if loss_function == "rank":
            self.loss_fct = RankLoss()
            self.loss_function = loss_function

    def compute_loss(self, model, inputs, return_outputs=False):
        # forward pass
        outputs = model(**inputs)
        logits = outputs.get("logits").view(-1, 2)
        if self.loss_function == "rank":
            loss = self.loss_fct(logits[:, 0], logits[:, 1])
        else:
            loss = self.loss_fct(logits, 
                torch.zeros(logits.shape[0], 
                    device=logits.device, 
                    dtype=torch.long))

        return (loss, outputs) if return_outputs else loss

    def _compute_loss(self, model, inputs):
        inputs = self._prepare_inputs(inputs)
        outputs = model(**inputs)
        logits = outputs.get("logits").view(-1, 2)
        if self.loss_function == "rank":
            loss = self.loss_fct(logits[:, 0], logits[:, 1])
        else:
            loss = self.loss_fct(logits, torch.zeros(logits.shape[0], device=logits.device, dtype=torch.long))

        return loss, logits

    def prediction_step(
        self,
        model: nn.Module,
        inputs: Dict[str, Union[torch.Tensor, Any]],
        prediction_loss_only: bool,
        ignore_keys: Optional[List[str]] = None,
    ) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[torch.Tensor]]:

        with torch.no_grad():
            # compute loss on predict data
            loss, logits = self._compute_loss(model, inputs)

        loss = loss.mean().detach()
        labels = torch.zeros(logits.shape[0], device=logits.device, dtype=torch.long)
        if self.args.prediction_loss_only:
            return (loss, None, None)

        return (loss, logits, labels)


def run_trainer(config_path: str):
    """
    Runs the trainer.

    ```
    from instructor.trainer import run_trainer

    config_path = "meta-opt-125m-freeze.yml"

    run_trainer(config_path=config_path)
    ```
    
    @param config_path: Path to the config file.
    """

    training_conf, training_args = argument_parsing(config_path)

    model = load_model(training_conf)

    tokenizer = get_tokenizer(training_conf["model_name"])

    train_datasets, evals = [], {}
    if "webgpt" in training_conf["datasets"]:
        web_dataset = WebGPT()
        train, eval = train_val_dataset(web_dataset)
        train_datasets.append(train)
        evals["webgpt"] = eval
    if "hfsummary" in training_conf["datasets"]:
        sum_train = HFSummary(split="train")
        train_datasets.append(sum_train)
        sum_eval = HFSummary(split="valid1")
        assert len(sum_eval) > 0
        evals["hfsummary"] = sum_eval
    train = ConcatDataset(train_datasets)
    collate_fn = DataCollatorForPairRank(
        tokenizer, max_length=training_conf["max_length"], 
        drop_token_type="galactica" in training_conf["model_name"]
    )
    assert len(evals) > 0

    trainer = RankTrainer(
        loss_function=training_conf["loss"],
        **dict(
            train_dataset=train,
            args=training_args,
            eval_dataset=evals,
            data_collator=collate_fn,
            tokenizer=tokenizer,
            compute_metrics=compute_metrics,
            model=model),
    )
    trainer.train()


if __name__ == "__main__":
    args = PARSER.parse_args()
    run_trainer(args.config)
