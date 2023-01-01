# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import evaluate
import numpy as np
import torch
from rank_datasets import DataCollatorForPairRank, HFSummary, WebGPT
from torch import nn
from torch.utils.data import ConcatDataset, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    DataCollator,
    EvalPrediction,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)
from utils import argument_parsing, freeze_top_n_layers, get_tokenizer, train_val_dataset

os.environ["WANDB_PROJECT"] = "reward-model"

accuracy = evaluate.load("accuracy")
parser = ArgumentParser()
parser.add_argument("config", type=str)


@dataclass
class CustomTrainingArguments(TrainingArguments):
    loss_function: str = "rank"


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
    def __init__(
        self,
        model: Union[PreTrainedModel, nn.Module] = None,
        args: TrainingArguments = None,
        data_collator: Optional[DataCollator] = None,
        train_dataset: Optional[Dataset] = None,
        eval_dataset: Optional[Dataset] = None,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        model_init: Callable[[], PreTrainedModel] = None,
        compute_metrics: Optional[Callable[[EvalPrediction], Dict]] = None,
        callbacks: Optional[List[TrainerCallback]] = None,
        optimizers: Tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.LambdaLR] = (None, None),
        preprocess_logits_for_metrics: Callable[[torch.Tensor, torch.Tensor], torch.Tensor] = None,
    ):
        super().__init__(
            model,
            args,
            data_collator,
            train_dataset,
            eval_dataset,
            tokenizer,
            model_init,
            compute_metrics,
            callbacks,
            optimizers,
            preprocess_logits_for_metrics,
        )
        self.loss_fct = RankLoss() if args.loss_function == "rank" else nn.CrossEntropyLoss()
        self.loss_function = args.loss_function

    def compute_loss(self, model, inputs, return_outputs=False):
        # forward pass
        outputs = model(**inputs)
        logits = outputs.get("logits").view(-1, 2)
        if self.loss_function == "rank":
            loss = self.loss_fct(logits[:, 0], logits[:, 1])
        else:
            loss = self.loss_fct(logits, torch.zeros(logits.shape[0], device=logits.device, dtype=torch.long))

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


if __name__ == "__main__":
    training_conf = argument_parsing(parser)

    model_name = training_conf["model_name"]
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1, problem_type="regression")
    if "freeze_layer" in training_conf:
        num_layer = training_conf["freeze_layer"]
        model = freeze_top_n_layers(model, num_layer)
        model_parameters = filter(lambda p: p.requires_grad, model.parameters())
        params = sum([np.prod(p.size()) for p in model_parameters])
        print("Number of trainable : {}M".format(int(params / 1e6)))

    tokenizer = get_tokenizer(model_name)
    args = CustomTrainingArguments(
        output_dir=f"{model_name}-finetuned",
        num_train_epochs=training_conf["num_train_epochs"],
        warmup_steps=500,
        loss_function=training_conf["loss"],
        learning_rate=training_conf["learning_rate"],
        # half_precision_backend="apex",
        fp16=True,
        gradient_checkpointing=training_conf["gradient_checkpointing"],
        gradient_accumulation_steps=training_conf["gradient_accumulation_steps"],
        per_device_train_batch_size=training_conf["per_device_train_batch_size"],
        per_device_eval_batch_size=training_conf["per_device_eval_batch_size"],
        weight_decay=0.01,
        max_grad_norm=2.0,
        logging_steps=10,
        save_total_limit=4,
        evaluation_strategy="steps",
        eval_steps=training_conf["eval_steps"],
        save_steps=1000,
        report_to="wandb",
    )
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
        tokenizer, max_length=training_conf["max_length"], drop_token_type="galactica" in model_name
    )
    assert len(evals) > 0
    trainer = RankTrainer(
        model,
        args,
        train_dataset=train,
        eval_dataset=eval,
        data_collator=collate_fn,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
