import argparse
import logging
import os
from typing import Callable, Dict, List, Literal, Optional, Tuple, Union

import bitsandbytes
import datasets
import torch
from model_training.custom_datasets.ranking_collator import RankingDataCollator
from model_training.efficiency_utils import fuse_gelu
from model_training.metrics import RewardMetrics
from model_training.utils import (
    PerDatasetSampler,
    _strtobool,
    get_dataset,
    get_loss,
    get_model,
    get_tokenizer,
    init_rng,
    read_yamls,
)
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import PreTrainedModel, Trainer, TrainingArguments
from transformers.trainer_pt_utils import IterableDatasetShard
from transformers.trainer_utils import seed_worker
from transformers.training_args import OptimizerNames
from transformers.utils import is_datasets_available


class RMTrainer(Trainer):
    def __init__(
        self,
        model: Union[PreTrainedModel, nn.Module] = None,
        args: TrainingArguments = None,
        sampler: torch.utils.data.sampler.Sampler = None,
        loss_function: Literal["RMLoss"] = "RMLoss",
        score_l2_reg: float = 0.001,
        train_collate_fn: Callable = None,
        **kwargs,
    ):
        super().__init__(model, args, **kwargs)
        self.train_collate_fn = train_collate_fn
        self.loss_fct = get_loss(loss_function, score_l2_reg=score_l2_reg)
        self.sampler = sampler

    def compute_loss(self, model, inputs, return_logits=False):
        batch, cu_lens = inputs

        logits = model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
        ).logits

        loss = self.loss_fct(logits, cu_lens)

        return (loss, logits) if return_logits else loss

    def prediction_step(
        self,
        model: nn.Module,
        inputs: Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor], List[int]],
        prediction_loss_only: bool,
        ignore_keys: Optional[List[str]] = None,
    ) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[torch.Tensor]]:
        batch, cu_lens = inputs
        with torch.no_grad():
            batch = self._prepare_inputs(batch)
            loss, logits = self.compute_loss(model, (batch, cu_lens), return_logits=True)

        loss = loss.mean().detach()

        labels = []
        for i, (s, e) in enumerate(zip(cu_lens[:-1], cu_lens[1:])):
            labels.extend([i] * (e - s))
        labels = torch.tensor(labels).view(-1, 1)
        return (loss, logits.T, labels.T)  # transposed to avoid truncation in evaluation_loop

    def get_train_dataloader(self):
        """
        Inject custom data sampling behaviour into training loop
        and use custom task mixing collate function : train_collate_fn

        rewrite from:
        https://github.com/huggingface/transformers/blob/67d074874d285e616393c65a0e670088e1b6b74a/src/transformers/trainer.py#L846
        """
        data_collator = self.train_collate_fn
        train_dataset = self.train_dataset
        if is_datasets_available() and isinstance(train_dataset, datasets.Dataset):
            train_dataset = self._remove_unused_columns(train_dataset, description="training")

        if isinstance(train_dataset, torch.utils.data.IterableDataset):
            # if we are using iterable dataset it means no weight sampling
            # added for backward compat
            if self.args.world_size > 1:
                train_dataset = IterableDatasetShard(
                    train_dataset,
                    batch_size=self._train_batch_size,
                    drop_last=self.args.dataloader_drop_last,
                    num_processes=self.args.world_size,
                    process_index=self.args.process_index,
                )
            return DataLoader(
                train_dataset,
                batch_size=self.args.per_device_train_batch_size,
                collate_fn=data_collator,
                num_workers=self.args.dataloader_num_workers,
                pin_memory=self.args.dataloader_pin_memory,
            )

        if self.sampler is None:
            train_sampler = self._get_train_sampler()
        else:
            train_sampler = self.sampler
            logging.warning("Custom sampler found!")

        dataloader = DataLoader(
            train_dataset,
            batch_size=self._train_batch_size,
            sampler=train_sampler,
            collate_fn=data_collator,
            drop_last=self.args.dataloader_drop_last,
            num_workers=self.args.dataloader_num_workers,
            pin_memory=self.args.dataloader_pin_memory,
            worker_init_fn=seed_worker,
        )
        return dataloader


def argument_parsing(notebook=False, notebook_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--local_rank", type=int, default=-1)
    parser.add_argument("--deepspeed", action="store_true")
    parser.add_argument("--no-deepspeed", dest="deepspeed", action="store_false")
    parser.add_argument("--wandb-entity", type=str, default="open-assistant")
    parser.add_argument("--rng_seed", type=int, help="rng seed")
    parser.set_defaults(deepspeed=False)

    if notebook:
        args, remaining = parser.parse_known_args(notebook_args)
    else:
        args, remaining = parser.parse_known_args()

    print(args)

    # Config from YAML
    conf = {}
    configs = read_yamls("./configs")
    for name in args.configs:
        if "," in name:
            for n in name.split(","):
                conf.update(configs[n])
        else:
            conf.update(configs[name])

    conf["wandb_entity"] = args.wandb_entity
    conf["local_rank"] = args.local_rank
    conf["deepspeed"] = args.deepspeed
    if args.rng_seed is not None:
        conf["rng_seed"] = args.rng_seed

    # get the world size in deeepspeed
    if conf["deepspeed"]:
        conf["world_size"] = int(os.getenv("WORLD_SIZE", default="1"))
    else:
        conf["world_size"] = 1

    # Override config from command-line
    parser = argparse.ArgumentParser()
    for key, value in conf.items():
        type_ = type(value) if value is not None else str
        if type_ == bool:
            type_ = _strtobool
        parser.add_argument(f"--{key}", type=type_, default=value)

    return parser.parse_args(remaining)


def main():
    training_conf = argument_parsing()

    init_rng(training_conf)

    tokenizer = get_tokenizer(training_conf)
    model = get_model(training_conf, tokenizer)

    train, evals = get_dataset(training_conf, mode="rm")
    train_collate_fn = RankingDataCollator(
        tokenizer,
        max_length=training_conf.max_length,
        pad_to_multiple_of=16,
    )
    eval_collate_fn = RankingDataCollator(
        tokenizer,
        max_length=training_conf.max_length,
        pad_to_multiple_of=16,
    )

    if training_conf.use_custom_sampler:
        sampler = PerDatasetSampler.build_sampler_from_config(
            training_conf,
            train.datasets,
            rank=training_conf.local_rank,
            world_size=training_conf.world_size,
            samples_length=list(
                map(
                    lambda x: train_collate_fn.process_one(x, return_length=True),
                    tqdm(train, desc="Calculating lengths per sample"),
                )
            )
            if training_conf.sort_by_length
            else None,
        )
    else:
        sampler = None

    optimizer = OptimizerNames.ADAMW_BNB if training_conf.quantization else OptimizerNames.ADAMW_HF

    if training_conf.quantization:
        for module in model.modules():
            if isinstance(module, torch.nn.Embedding):
                bitsandbytes.optim.GlobalOptimManager.get_instance().register_module_override(
                    module, "weight", {"optim_bits": 32}
                )

    if training_conf.fuse_gelu:
        model = fuse_gelu(model)

    output_dir = (
        training_conf.output_dir
        if training_conf.output_dir
        else f"{training_conf.model_name}-{training_conf.log_dir}-finetuned"
    )

    args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=training_conf.num_train_epochs,
        warmup_steps=training_conf.warmup_steps,
        learning_rate=float(training_conf.learning_rate),
        deepspeed="configs/zero_config.json" if training_conf.deepspeed else None,
        optim=optimizer,
        fp16=training_conf.fp16,
        local_rank=training_conf.local_rank,
        gradient_checkpointing=training_conf.gradient_checkpointing,
        gradient_accumulation_steps=training_conf.gradient_accumulation_steps,
        per_device_train_batch_size=training_conf.per_device_train_batch_size,
        per_device_eval_batch_size=training_conf.per_device_eval_batch_size,
        adam_beta1=training_conf.adam_beta1,
        adam_beta2=training_conf.adam_beta2,
        adam_epsilon=float(training_conf.adam_epsilon),
        weight_decay=training_conf.weight_decay,
        max_grad_norm=training_conf.max_grad_norm,
        logging_steps=training_conf.logging_steps,
        save_total_limit=training_conf.save_total_limit,
        evaluation_strategy="steps",
        eval_steps=training_conf.eval_steps,
        save_steps=training_conf.save_steps,
        eval_accumulation_steps=training_conf.eval_accumulation_steps,
        report_to="wandb" if training_conf.log_wandb else None,
    )

    if not training_conf.log_wandb:
        os.environ["WANDB_MODE"] = "offline"

    if training_conf.log_wandb and (not training_conf.deepspeed or training_conf.local_rank == 0):
        import wandb

        wandb.init(
            project="reward-model",
            entity=training_conf.wandb_entity,
            name=f"{training_conf.model_name}-{training_conf.log_dir}-rm",
            config=training_conf,
        )
    compute_metrics = RewardMetrics(training_conf.metrics)
    trainer = RMTrainer(
        model=model,
        args=args,
        sampler=sampler,
        train_collate_fn=train_collate_fn,
        loss_function=training_conf.loss_fn,
        score_l2_reg=training_conf.score_l2_reg,
        train_dataset=train,
        eval_dataset=evals,
        data_collator=eval_collate_fn,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)


if __name__ == "__main__":
    main()
