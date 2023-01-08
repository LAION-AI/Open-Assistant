import os
from argparse import ArgumentParser
from typing import Any, Dict, List, Optional, Tuple, Union

import evaluate
import numpy as np
import torch
from models import RankGenModel
from rank_datasets import DataCollatorForPairRank, RankGenCollator
from torch import nn
from transformers import (
    AdamW,
    AutoModelForSequenceClassification,
    PreTrainedModel,
    Trainer,
    TrainingArguments,
    get_cosine_schedule_with_warmup,
    get_linear_schedule_with_warmup,
)
from utils import argument_parsing, freeze_top_n_layers, get_datasets, get_tokenizer

os.environ["WANDB_PROJECT"] = "reward-model"

accuracy = evaluate.load("accuracy")
parser = ArgumentParser()
parser.add_argument("config", type=str)


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
        loss = -self.log_sigmoid(pos - neg + self.eps).mean()
        return loss


class RankTrainer(Trainer):
    def __init__(
        self,
        model: Union[PreTrainedModel, nn.Module] = None,
        model_name: str = None,
        args: Optional[TrainingArguments] = None,
        loss_function: str = "rank",
        **kwargs,
    ):
        super().__init__(model, args, **kwargs)
        self.loss_fct = RankLoss() if loss_function == "rank" else nn.CrossEntropyLoss()
        self.loss_function = loss_function
        self.model_name = model_name

    def compute_loss(self, model, inputs, return_outputs=False):
        # forward pass
        if "rankgen" in self.model_name:
            positive_outputs = model(inputs["prefix"], inputs["positive"])
            negative_outputs = model(inputs["prefix"], inputs["negative"])
            if self.loss_function == "rank":
                loss = self.loss_fct(positive_outputs, negative_outputs)
            else:
                raise NotImplementedError("Only ranking loss has been implemented for rankgen model")
            outputs = torch.hstack((positive_outputs, negative_outputs))  # logits
        else:
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
        with torch.inference_mode():
            if "rankgen" in self.model_name:
                inputs = self._prepare_inputs(inputs)
                positive_outputs = model(inputs["prefix"], inputs["positive"])
                negative_outputs = model(inputs["prefix"], inputs["negative"])
                if self.loss_function == "rank":
                    loss = self.loss_fct(positive_outputs, negative_outputs)
                else:
                    raise NotImplementedError("Only ranking loss has been implemented for rankgen model")
                outputs = torch.hstack((positive_outputs, negative_outputs))  # logits
                return (loss, outputs, None)
            else:
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
    if "rankgen-t5" in model_name:
        model = RankGenModel(model_name)
    else:
        model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1, problem_type="regression")
    if "freeze_layer" in training_conf:
        num_layer = training_conf["freeze_layer"]
        model = freeze_top_n_layers(model, num_layer)
        model_parameters = filter(lambda p: p.requires_grad, model.parameters())
        params = sum([np.prod(p.size()) for p in model_parameters])
        print("Number of trainable : {}M".format(int(params / 1e6)))

    args = TrainingArguments(
        output_dir=f"{model_name}-finetuned",
        num_train_epochs=training_conf["num_train_epochs"],
        warmup_steps=500,
        learning_rate=training_conf["learning_rate"],
        # half_precision_backend="apex",
        fp16=training_conf["fp16"],
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

    tokenizer = get_tokenizer(training_conf["tokenizer_name"])
    train, evals = get_datasets(training_conf["datasets"])
    if "rankgen" in model_name:
        collate_fn = RankGenCollator(tokenizer, max_length=training_conf["max_length"])
    else:
        collate_fn = DataCollatorForPairRank(tokenizer, max_length=training_conf["max_length"])
    assert len(evals) > 0

    optimizer = AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    scheduler = None
    if "scheduler" in training_conf:
        if training_conf["scheduler"] == "linear":
            scheduler = get_linear_schedule_with_warmup()
        elif training_conf["scheduler"] == "cosine":
            scheduler = get_cosine_schedule_with_warmup(
                optimizer,
                num_warmup_steps=args.warmup_steps,
                num_training_steps=len(train)
                * args.num_train_epochs
                / (args.per_device_train_batch_size * args.gradient_accumulation_steps),
            )

    trainer = RankTrainer(
        model=model,
        model_name=model_name,
        args=args,
        loss_function=training_conf["loss"],
        train_dataset=train,
        eval_dataset=evals,
        data_collator=collate_fn,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        optimizers=(optimizer, scheduler),
    )
    # trainer.evaluate()
    trainer.train()
