import argparse
import os
from distutils.util import strtobool
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from torch import nn
from torch.utils.data import Dataset
from transformers import PreTrainedModel, Trainer, TrainingArguments, get_cosine_schedule_with_warmup
from utils import get_dataset, get_loss, get_model, get_tokenizer, read_yamls

os.environ["WANDB_PROJECT"] = "supervised-finetuning"


def compute_metrics(eval_pred):
    pred_ids = eval_pred.predictions
    labels = eval_pred.label_ids

    return {"accuracy": (pred_ids[labels > 0] == labels[labels > 0]).mean()}


def preprocess_logits_for_metrics(logits, labels):
    pred_ids = torch.argmax(logits, dim=-1)
    return pred_ids


class SFTTrainer(Trainer):
    def __init__(
        self,
        model: Union[PreTrainedModel, nn.Module] = None,
        args: TrainingArguments = None,
        loss_function: str = "CrossEntropyLoss",
        **kwargs,
    ):
        super().__init__(model, args, **kwargs)

        # By default CrossEntropyLoss ignores padding_index -100, but just in case use our own loss_fct
        self.loss_fct = get_loss(loss_function)

    def fetch_scheduler(self):
        return get_cosine_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.args.warmup_steps,
            num_training_steps=self.num_train_steps,
            num_cycles=1,
            last_epoch=-1,
        )

    def compute_loss(self, model, inputs, return_outputs=False):
        labels_mask = inputs.pop("label_masks")

        outputs = model(**inputs)

        loss = self.loss_fct(outputs.get("logits"), torch.roll(inputs["input_ids"], -1, -1), mask=labels_mask)

        return (loss, outputs) if return_outputs else loss

    def _compute_loss(self, model, inputs):

        labels_mask = inputs.pop("label_masks")

        inputs = self._prepare_inputs(inputs)

        outputs = model(**inputs)

        logits = outputs.get("logits")

        targets = torch.roll(inputs["input_ids"], -1, -1)
        loss = self.loss_fct(outputs.get("logits"), targets, mask=labels_mask)

        return loss, logits, targets, labels_mask

    def prediction_step(
        self,
        model: nn.Module,
        inputs: Dict[str, Union[torch.Tensor, Any]],
        prediction_loss_only: bool,
        ignore_keys: Optional[List[str]] = None,
    ) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[torch.Tensor]]:

        with torch.no_grad():
            loss, logits, labels, labels_mask = self._compute_loss(model, inputs)
            labels[~labels_mask] = -100  # padding_index

        loss = loss.mean().detach()

        if self.args.prediction_loss_only:
            return (loss, None, None)

        return (loss, logits, labels)


def _strtobool(x):
    return bool(strtobool(x))


def argument_parsing(notebook=False, notebook_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--local_rank", type=int, default=-1)
    parser.add_argument("--deepspeed", action="store_true")
    parser.add_argument("--no-deepspeed", dest="deepspeed", action="store_false")
    parser.set_defaults(deepspeed=False)

    if notebook:
        args, remaining = parser.parse_known_args(notebook_args)
    else:
        args, remaining = parser.parse_known_args()

    # Config from YAML
    conf = {}
    configs = read_yamls("./configs")
    for name in args.configs:
        if "," in name:
            for n in name.split(","):
                conf.update(configs[n])
        else:
            conf.update(configs[name])

    conf["local_rank"] = args.local_rank
    conf["deepspeed"] = args.deepspeed
    # Override config from command-line
    parser = argparse.ArgumentParser()
    for key, value in conf.items():
        type_ = type(value) if value is not None else str
        if type_ == bool:
            type_ = _strtobool
        parser.add_argument(f"--{key}", type=type_, default=value)

    return parser.parse_args(remaining)


if __name__ == "__main__":
    training_conf = argument_parsing()

    tokenizer = get_tokenizer(training_conf)
    model = get_model(training_conf, tokenizer)

    train, evals, collate_fn = get_dataset(training_conf, tokenizer)

    args = TrainingArguments(
        output_dir=f"{training_conf.model_name}-{training_conf.log_dir}-finetuned",
        num_train_epochs=training_conf.num_train_epochs,
        warmup_steps=training_conf.warmup_steps,
        learning_rate=float(training_conf.learning_rate),
        deepspeed="configs/zero_config.json" if training_conf.deepspeed else None,
        fp16=True,
        local_rank=training_conf.local_rank,
        gradient_checkpointing=training_conf.gradient_checkpointing,
        gradient_accumulation_steps=training_conf.gradient_accumulation_steps,
        per_device_train_batch_size=training_conf.per_device_train_batch_size,
        per_device_eval_batch_size=training_conf.per_device_eval_batch_size,
        weight_decay=training_conf.weight_decay,
        max_grad_norm=training_conf.max_grad_norm,
        logging_steps=training_conf.logging_steps,
        save_total_limit=training_conf.save_total_limit,
        evaluation_strategy="steps",
        eval_steps=training_conf.eval_steps,
        save_steps=training_conf.save_steps,
        eval_accumulation_steps=training_conf.eval_accumulation_steps,
        report_to="wandb",
    )

    assert len(evals) > 0
    trainer = SFTTrainer(
        model,
        args,
        loss_function=training_conf.loss_fn,
        train_dataset=train,
        eval_dataset=evals,
        data_collator=collate_fn,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        preprocess_logits_for_metrics=preprocess_logits_for_metrics,
    )
    trainer.train()
