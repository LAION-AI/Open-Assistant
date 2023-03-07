import torch
from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer, 
    EvalPrediction,
    DataCollator,
    Trainer,
    TrainingArguments)
import os
from omegaconf import DictConfig, OmegaConf
import hydra
from hydra.utils import instantiate
from utils import add_special_tokens
from datasets import load_dataset
from custom_datasets.rot_dataset import SafetyDataset, SafetyDataCollator


@hydra.main(version_base=None, config_path="config",config_name="config")
def train(cfg: DictConfig) -> None:
    
    if not os.path.exists(cfg.save_folder):
        os.mkdir(cfg.save_folder)

    model = T5ForConditionalGeneration.from_pretrained(cfg.model)
    tokenizer = T5Tokenizer.from_pretrained(cfg.model,padding_side=cfg.padding_side,truncation_side=cfg.truncation_side,model_max_length=model.config.n_positions)
    add_special_tokens(cfg.special_tokens,tokenizer,model)
    training_args = instantiate(cfg.trainer)

    dataset = load_dataset(cfg.dataset.name)
    train_dataset = SafetyDataset(dataset,split=OmegaConf.to_object(cfg.dataset.train),tokenizer=tokenizer,max_len=cfg.max_length)
    valid_dataset = SafetyDataset(dataset,split=cfg.dataset.test,tokenizer=tokenizer,max_len=cfg.max_length)

    # Initialize our Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        data_collator=SafetyDataCollator()
    )

    # Training
    trainer.train()

    trainer.save_model(os.path.join(cfg.save_folder,f"{cfg.model_name}-model"))
    tokenizer.save_vocabulary(os.path.join(cfg.save_folder,f"{cfg.model_name}-tokenizer"))


if __name__ == "__main__":

    train()
