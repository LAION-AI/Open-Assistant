# -*- coding: utf-8 -*-
import re
import os
from typing import Dict, Any, Optional, Tuple
from argparse import ArgumentParser

import numpy as np
import yaml
from sklearn.model_selection import train_test_split
from torch.utils.data import Subset
from torch.nn.modules.container import ModuleList
from transformers import (
    AutoTokenizer, 
    TrainingArguments, 
    AutoModelForSequenceClassification
)


re_reference_remove = re.compile(r"\[\d+(?:,\s*\d+)*?\]")


DEFAULT_PARAMS = dict(
    warmup_steps=500,
    num_train_epochs=4,
    learning_rate=3e-5,
    eval_steps=500,
    loss="rank",
    max_length=440,
    per_device_eval_batch_size=5,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=8,
    gradient_checkpointing=False,
    datasets=["webgpt"],
    fp16=True,
    weight_decay=0.01,
    max_grad_norm=2.0,
    logging_steps=10,
    save_total_limit=4,
    evaluation_strategy="steps",
    save_steps=1000,
    report_to="wandb",
)


__DEFAULT_PARAMS_TYPES = dict(
    warmup_steps=int,
    weight_decay=float,
    max_grad_norm=float,
    logging_steps=int,
    save_total_limit=int,
    num_train_epochs=int,
    learning_rate=float,
    eval_steps=int,
    max_length=int,
    per_device_eval_batch_size=int,
    per_device_train_batch_size=int,
    gradient_accumulation_steps=int,
    save_steps=int,
)


# Config parameters that are not passed to the TrainingArguments
EXTRA_PARAMS  = ('loss', 'max_length', 'datasets', 
              'model_name', "freeze_layer")


def webgpt_return_format(row):
    res = {"question": row["question"]["full_text"]}
    row["answer_0"] = re_reference_remove.sub("", row["answer_0"])
    row["answer_1"] = re_reference_remove.sub("", row["answer_1"])

    if row["score_0"] >= row["score_1"]:
        res["pos"] = row["answer_0"]
        res["neg"] = row["answer_1"]
        return res

    res["pos"] = row["answer_1"]
    res["neg"] = row["answer_0"]
    return res


def get_tokenizer(tokenizer_name):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name,
                                              use_fast="galactica" not in tokenizer_name)
    if "galactica" in tokenizer_name:
        tokenizer.add_special_tokens({"pad_token": "<pad>", "eos_token": "</s>"})
    
    return tokenizer


def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    # [3879, 11479, 8341, 9177, 10798, 18177, 5735, 15669, 4837, 2760]
    print(val_idx[:10])
    # [13582, 5919, 11875, 7373, 19135, 13706, 8555, 15788, 15005, 15209]
    print(train_idx[:10])
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def freeze_top_n_layers(model, target_layers: int):
    """
    Sets to False the `requires_grad` attribute of the first `target_layers` 
    number of layers

    @param model: the model to be frozen
    @param target_layers: the number of layers to be frozen

    @return: the partially frozen model
    """
    # its possible we can simply detect which module is a ModuleList
    # and simply freeze the module without doing string parsing

    # This should do just that ^

    # Freeze embedding layers
    for name, param in model.named_parameters():
        if "embed" in name:
            param.requires_grad = False
    
    # Freeze the first `target_layers` number of layers
    for _,module in model.named_modules():
        if isinstance(module, ModuleList):
            for pname, param in module.named_parameters():
                if int(pname.split(".")[0]) < target_layers:
                    param.requires_grad = False
        
    return model


def load_model(training_conf: Dict[str, Any]):
    """
    Loads a model using a name from the training config dictionary returned
    by the `argument_parsing` function.

    Returns the model object.

    @param training_conf: the training config dictionary.
    """
    
    model_name = training_conf["model_name"]
    model = AutoModelForSequenceClassification.from_pretrained(model_name, 
        num_labels=1, 
        problem_type="regression")
    if "freeze_layer" in training_conf:
        num_layer = training_conf["freeze_layer"]
        model = freeze_top_n_layers(model, num_layer)

    return model
    

def argument_parsing(config_path: str,
        output_dir: Optional[str] = None,
        default_params: Optional[Dict[str, Any]] = DEFAULT_PARAMS,
        extra_params: Optional[Tuple] = EXTRA_PARAMS) -> \
            Tuple[Dict[str, Any], TrainingArguments]:
    """
    Collects default parameters and the ones from a config file into a dict,
    returning the dictionary with full options and a TrainingArguments object.

    All parameters have sensible defaults.

    This function returns a dictionary of all parameters and a ready to use
    TrainingArguments object.
    
    @param config_path: path to the config file with training parameters .
    @param output_dir: (optional) path to the output directory if you want to change it.
    @param default_params: (optional) default training parameters. Default:
        utils.DEFAULT_PARAMS
    @param extra_params: (optional) extra parameters that are not passed to the 
        TrainingArguments object. Default: utils.EXTRA_PARAMS
    """

    with open(config_path, "r", encoding="utf-8") as f:
        training_conf = yaml.safe_load(f.read())
    model_name = training_conf["model_name"]

    # Merge config params with defaults and fix types
    
    args_dict = {**default_params, \
        **{k: __DEFAULT_PARAMS_TYPES.get(k, lambda x: x)(v)
            for k, v in training_conf.items()}}
    
    default_dir = os.path.normpath(f"{model_name}-finetuned")
    default_dir = "-".join(os.path.split(default_dir))
    output_dir = output_dir or default_dir
    args_dict["output_dir"] = output_dir

    train_args = TrainingArguments(**{k: v for k, v in args_dict.items() 
        if k not in extra_params})
    return args_dict, train_args


if __name__ == "__main__":
    from transformers import AutoModelForSequenceClassification

    model = AutoModelForSequenceClassification.from_pretrained("bigscience/bloomz-560m")
    freeze_top_n_layers(model, 10)
    print(model.state_dict().keys())
