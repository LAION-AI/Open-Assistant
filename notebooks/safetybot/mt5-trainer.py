import torch
from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer, 
    EvalPrediction,
    DataCollator,
    Trainer,
    TrainingArguments)
from datasets import load_dataset,concatenate_datasets
from torch.utils.data import Dataset, DataLoader
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import wandb
import os

jobid = os.environ.get("SLURM_JOB_ID")
ROOT_DIR = os.path.join("/scratch/c.scmse/safety",jobid)

LABEL2ID = {
    "__casual__": "0",
    "__needs_caution__": "1",
    "__needs_intervention__": "2",
    "__probably_needs_caution__": "3",
    "__possibly_needs_caution__": "4",
}

SPECIAL_TOKENS = {"context_token":"<ctx>","sep_token":"<sep>","label_token":"<cls>","rot_token":"<rot>"}

wandb_key = json.load(open("/home/c.scmse/credentials/wandb.json" ))["key"]

wandb.login(key=wandb_key)


CONFIG = {"special_tokens":SPECIAL_TOKENS,
"model":"t5-base",
"max_len":256,
"train":["train","validation"],
"test":"test",
"lr":1e-5,
"epochs":1,
"train_dataset":"allenai/prosocial-dialog",
"Notes":"using train+validation"
}

def add_special_tokens(tokenizer,model):
    for key,value in SPECIAL_TOKENS.items():
        setattr(tokenizer,key,value)
        tokenizer.add_tokens([value])
        setattr(tokenizer,key+"_id",tokenizer.encode(value)[0])

    model.resize_token_embeddings(len(tokenizer))


class SafetyDataset(Dataset):
    
    def __init__(self,dataset,split,tokenizer,max_len=512):
        
        super().__init__()

        if isinstance(split,List):
            self.split = "-".join(split)
            self.dataset = concatenate_datasets([dataset[sp] for sp in split])
        else:
            self.split = split
            self.dataset = dataset[split]

        self.max_len = max_len
        self.tokenizer = tokenizer
        self.label2id = LABEL2ID
        
        
    def __len__(self):
        
        return len(self.dataset)
    
    def __getitem__(self,idx):
        
        
        idx_start = idx
        end = self.dataset[max(0, idx_start - 1)]["episode_done"]
        while (not end) and (idx_start > 0):
            end = self.dataset[max(0, idx_start - 2)]["episode_done"]
            idx_start -= 1
        idx_start = max(0, idx_start)
        context = [f'User: {self.dataset[i]["context"]}\n bot:{self.dataset[i]["response"]}' for i in range(idx_start, idx)]
        context = self.tokenizer.sep_token.join(context)
        rots = self.dataset[idx]["rots"]
        label = self.label2id[self.dataset[idx]["safety_label"]]
        input_tokens = self.tokenizer.encode(self.dataset[idx]["context"],add_special_tokens=False)
        max_len = self.max_len - (len(input_tokens)+2)
        context = self.tokenizer.encode(context,
                                add_special_tokens=False,
                               max_length=max_len,
                               )
        rots = self.tokenizer.sep_token.join(rots)
        input_ids = input_tokens + [self.tokenizer.context_token_id] + context + [self.tokenizer.eos_token_id]
        input_ids = input_ids + [self.tokenizer.pad_token_id] * max(0,(self.max_len - len(input_ids)))
        mask = [1]*len(input_ids) + [self.tokenizer.pad_token_id] * (self.max_len-len(input_ids))
        target_text = self.tokenizer.label_token + label + self.tokenizer.context_token + rots
        decoder_ids = self.tokenizer(target_text,
                                add_special_tokens=True,
                               max_length=self.max_len,
                               padding='max_length',
                               )
        
        return {
            "input_ids":torch.LongTensor(input_ids),
            "attention_mask":torch.LongTensor(mask),
            "decoder_input_ids":torch.LongTensor(decoder_ids["input_ids"]),
            "decoder_attention_mask":torch.LongTensor(decoder_ids["attention_mask"]),
        }
        
        
        
# This dataclass implementation is taken from Suraj Patil: https://github.com/patil-suraj/question_generation
@dataclass
class T2TDataCollator():
  def __call__(self, batch: List) -> Dict[str, torch.Tensor]:
    """
    Take a list of samples from a Dataset and collate them into a batch.
    Returns:
    A dictionary of tensors
    """
    
    input_ids = torch.stack([example['input_ids'] for example in batch])
    lm_labels = torch.stack([example['decoder_input_ids'] for example in batch])
    lm_labels[lm_labels[:, :] == 0] = -100 
    attention_mask = torch.stack([example['attention_mask'] for example in batch])
    decoder_attention_mask = torch.stack([example['decoder_attention_mask'] for example in batch])
    
    return {
        'input_ids': input_ids, 
        'attention_mask': attention_mask,
        'labels': lm_labels, 
        'decoder_attention_mask': decoder_attention_mask
    }



if __name__ == "__main__":

    if not os.path.exists(ROOT_DIR):
        os.mkdir(ROOT_DIR)
    
    with open(os.path.join(ROOT_DIR,"config.json"),"w") as file:
        json.dump(json.dumps(CONFIG),file)
    
    dataset = load_dataset(CONFIG["train_dataset"])

    model = T5ForConditionalGeneration.from_pretrained(CONFIG["model"])
    tokenizer = T5Tokenizer.from_pretrained(CONFIG["model"],padding_side="right",truncation_side="right",model_max_length=512)
    add_special_tokens(tokenizer,model)
    train_dataset = SafetyDataset(dataset,split=CONFIG["train"],tokenizer=tokenizer,max_len=CONFIG["max_len"])
    valid_dataset = SafetyDataset(dataset,split=CONFIG["test"],tokenizer=tokenizer,max_len=CONFIG["max_len"])
    training_args = TrainingArguments(output_dir=ROOT_DIR, 
                                  per_device_train_batch_size=8, 
                                  per_device_eval_batch_size=8,
#                                   gradient_accumulation_steps=16,
                                  learning_rate=CONFIG["lr"], 
                                  num_train_epochs=CONFIG["epochs"],
                                  logging_steps=100,
                                  evaluation_strategy="steps",
                                  eval_steps=1000,
                                  save_steps=5000,
                                  report_to="wandb",
                                  push_to_hub=False,
                                  fp16=True,
                                  run_name=f"safety-bot-sample-hawk-{jobid}",)


    # Initialize our Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        data_collator=T2TDataCollator()
    )

    # Training
    trainer.train()

    # When training is done, we push the fine-tuned model to the Hub
    #trainer.push_to_hub("t5-end2end-questions-generation")

    wandb.finish()
    #trainer.save_model(os.path.join(ROOT_DIR,"safety-model"))
    tokenizer.save_vocabulary(os.path.join(ROOT_DIR,"safety-tokenizer"))