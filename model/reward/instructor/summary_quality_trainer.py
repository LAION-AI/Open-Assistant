import os
from argparse import ArgumentParser
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import evaluate
import numpy as np
import torch
from experimental_dataset import DataCollatorForSummaryScore, HFSummaryQuality
from torch import nn
from torch.utils.data import Dataset
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
from utils import argument_parsing, freeze_top_n_layers, get_tokenizer

os.environ["WANDB_PROJECT"] = "quality-scoring"

parser = ArgumentParser()
parser.add_argument("config", type=str)

accuracy = evaluate.load("mse")


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    return accuracy.compute(predictions=predictions.flatten(), references=labels.flatten())


class QualityTrainer(Trainer):
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
        self.loss_fct = nn.L1Loss()
        self.sigmoid = nn.Sigmoid()

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        # forward pass
        outputs = model(**inputs)
        logits = self.sigmoid(outputs.get("logits"))
        loss = self.loss_fct(logits, labels)

        return (loss, outputs) if return_outputs else loss

    def _compute_loss(self, model, inputs):
        inputs = self._prepare_inputs(inputs)
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = self.sigmoid(outputs.get("logits"))
        loss = self.loss_fct(logits, labels)

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
        labels = inputs["labels"]
        if self.args.prediction_loss_only:
            return (loss, None, None)

        return (loss, logits, labels)


if __name__ == "__main__":
    training_conf = argument_parsing(parser)

    model_name = training_conf["model_name"]
    tokenizer = get_tokenizer(model_name)
    collate_fn = DataCollatorForSummaryScore(
        tokenizer, max_length=training_conf["max_length"], drop_token_type="galactica" in model_name
    )
    train = HFSummaryQuality(split="validation", tokenizer=tokenizer, max_length=training_conf["max_length"])
    eval = HFSummaryQuality(split="test", tokenizer=tokenizer, max_length=training_conf["max_length"])
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=len(train.label2idx), problem_type="regression"
    )

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
    trainer = QualityTrainer(
        model,
        args,
        train_dataset=train,
        eval_dataset=eval,
        data_collator=collate_fn,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
