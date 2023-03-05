import os
from argparse import ArgumentParser
from typing import Any, Dict, List, Optional, Tuple, Union

import evaluate
import numpy as np
import torch
from models import RankGenModel
from rank_datasets import DataCollatorForPairRank, RankGenCollator
from torch import nn
from transformers import AutoModelForSequenceClassification, PreTrainedModel, Trainer, TrainingArguments
from transformers.training_args import OptimizerNames
from utils import argument_parsing, freeze_top_n_layers, get_datasets, get_tokenizer

os.environ["WANDB_PROJECT"] = "reward-model"

accuracy = evaluate.load("accuracy")
parser = ArgumentParser()
parser.add_argument("config", type=str)
parser.add_argument("--local_rank", type=int, default=-1)
parser.add_argument("--deepspeed", action="store_true")
parser.set_defaults(deepspeed=False)
parser.add_argument("--no-deepspeed", dest="deepspeed", action="store_false")
parser.add_argument("--wandb-entity", type=str, default="open-assistant")
parser.add_argument("--output_dir", type=str, default=None)


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
            outputs = torch.hstack((positive_outputs[:, None], negative_outputs[:, None]))
        else:
            inputs.pop("token_type_ids", None)
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
                logits = torch.hstack((positive_outputs[:, None], negative_outputs[:, None]))
                # Create labels which are not None so HF will call compute_metrics:
                labels = torch.zeros(logits.shape[0], device=logits.device, dtype=torch.long)
                return loss, logits, labels
            else:
                loss, logits = self._compute_loss(model, inputs)

                loss = loss.mean().detach()
                labels = torch.zeros(logits.shape[0], device=logits.device, dtype=torch.long)
                if self.args.prediction_loss_only:
                    return loss, None, None

                return loss, logits, labels


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

    optimizer = OptimizerNames.ADAMW_HF
    args = TrainingArguments(
        output_dir=training_conf["output_dir"],
        num_train_epochs=training_conf["num_train_epochs"],
        warmup_steps=training_conf["warmup_steps"],
        optim=optimizer,
        # lr_scheduler_type=training_conf["scheduler"],
        learning_rate=training_conf["learning_rate"],
        # half_precision_backend="apex",
        deepspeed="configs/zero_config.json" if training_conf["deepspeed"] else None,
        fp16=training_conf["fp16"],
        local_rank=training_conf["local_rank"],
        gradient_checkpointing=training_conf["gradient_checkpointing"],
        gradient_accumulation_steps=training_conf["gradient_accumulation_steps"],
        per_device_train_batch_size=training_conf["per_device_train_batch_size"],
        per_device_eval_batch_size=training_conf["per_device_eval_batch_size"],
        weight_decay=training_conf["weight_decay"],
        max_grad_norm=training_conf["max_grad_norm"],
        logging_steps=10,
        save_total_limit=4,
        evaluation_strategy="steps",
        eval_steps=training_conf["eval_steps"],
        save_steps=training_conf["save_steps"],
        report_to="wandb",
    )

    tokenizer = get_tokenizer(training_conf["tokenizer_name"])
    train, evals = get_datasets(training_conf["datasets"], tokenizer)
    if "rankgen" in model_name:
        collate_fn = RankGenCollator(tokenizer, max_length=training_conf["max_length"])
    else:
        collate_fn = DataCollatorForPairRank(
            tokenizer,
            max_length=training_conf["max_length"],
            drop_token_type=training_conf.get("drop_token_type", False),
        )
    assert len(evals) > 0

    if not training_conf["deepspeed"] or training_conf["local_rank"] == 0:
        import wandb

        wandb.init(
            project=os.environ["WANDB_PROJECT"], name=f"{model_name}-finetuned", entity=training_conf["wandb_entity"]
        )

    trainer = RankTrainer(
        model=model,
        model_name=model_name,
        args=args,
        loss_function=training_conf["loss"],
        train_dataset=train,
        eval_dataset=torch.utils.data.ConcatDataset(evals.values()),
        data_collator=collate_fn,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        # optimizers=(optimizer, scheduler),
    )
    trainer.train()
    trainer.evaluate()
