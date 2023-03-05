import re
from typing import AnyStr, List

import yaml
from sklearn.model_selection import train_test_split
from torch.utils.data import Subset
from transformers import AutoTokenizer, T5Tokenizer

# @agoryuno contributed this
re_reference_remove = re.compile(r"\[\d+(?:,\s*\d+)*?\]")


def webgpt_return_format(row):
    if row["score_0"] >= row["score_1"]:
        # remove this to prevent information leak, since we are not using reference
        return {
            "question": row["question"]["full_text"],
            "pos": re_reference_remove.sub("", row["answer_0"]),
            "neg": re_reference_remove.sub("", row["answer_1"]),
        }

    return {
        "question": row["question"]["full_text"],
        "pos": re_reference_remove.sub("", row["answer_1"]),
        "neg": re_reference_remove.sub("", row["answer_0"]),
    }


def get_tokenizer(tokenizer_name):
    if "t5" in tokenizer_name:  # rankgen
        tokenizer = T5Tokenizer.from_pretrained(tokenizer_name, truncation_side="left")
    else:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
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


def freeze_top_n_layers(model, target_layers):
    # its possible we can simply detect which module is a ModuleList
    # and simply freeze the module without doing string parsing
    for name, param in model.named_parameters():
        if "embed" in name:
            param.requires_grad = False
        elif ".layer" in name or ".h." in name:
            tokens = name.split(".")
            idx = 0
            for token in tokens:
                if "layer" in token or token == "h":
                    break
                idx += 1
            if idx >= len(tokens):
                continue

            layer_ = int(tokens[idx + 1])
            if layer_ < target_layers:
                # print('freeze ', layer_, name)
                param.requires_grad = False
    return model


def argument_parsing(parser):
    args = parser.parse_args()
    with open(args.config, "r", encoding="utf-8") as f:
        training_conf = yaml.safe_load(f.read())

    default_params = {
        "num_train_epochs": 4,
        "learning_rate": 3e-5,
        "eval_steps": 500,
        "loss": "rank",
        "warmup_steps": 500,
        "max_length": 440,
        "weight_decay": 0.01,
        "max_grad_norm": 2.0,
        "save_steps": 500,
        "per_device_eval_batch_size": 5,
        "per_device_train_batch_size": 8,
        "gradient_accumulation_steps": 8,
        "gradient_checkpointing": False,
        "deepspeed": args.deepspeed,
        "local_rank": args.local_rank,
        "datasets": ["webgpt"],
        "wandb_entity": args.wandb_entity,
        "fp16": True,
        "tokenizer_name": training_conf["model_name"],
        "output_dir": "output",
    }

    params = {**default_params, **training_conf}
    for name in [
        "gradient_accumulation_steps",
        "num_train_epochs",
        "save_steps",
        "eval_steps",
        "per_device_train_batch_size",
        "per_device_eval_batch_size",
    ]:
        params[name] = int(params[name])
    for name in ["learning_rate", "weight_decay", "max_grad_norm"]:
        params[name] = float(params[name])

    if args.output_dir:
        params["output_dir"] = args.output_dir

    return params


def get_datasets(dataset_list: List[AnyStr], tokenizer):
    from rank_datasets import AnthropicRLHF, GPTJSynthetic, HFSummary, OAPrivate, WebGPT
    from torch.utils.data import ConcatDataset

    train_datasets, evals = [], {}
    for dataset_name in dataset_list:
        if "webgpt" == dataset_name:
            web_dataset = WebGPT()
            train, eval = train_val_dataset(web_dataset, 0.2)
            train_datasets.append(train)
            evals["webgpt"] = eval
        elif "hfsummary" == dataset_name:
            sum_train = HFSummary(split="train")
            train_datasets.append(sum_train)
            sum_eval = HFSummary(split="valid1")
            assert len(sum_eval) > 0
            evals["hfsummary"] = sum_eval
        elif "gptsynthetic" == dataset_name:
            dataset = GPTJSynthetic()
            train, eval = train_val_dataset(dataset, 0.1)
            train_datasets.append(train)
            evals["gptsynthetic"] = eval
        elif "anthropic_rlhf" == dataset_name:
            train = AnthropicRLHF("train", tokenizer.sep_token)
            eval = AnthropicRLHF("test", tokenizer.sep_token)
            train_datasets.append(train)
            evals["anthropic_rlhf"] = eval
        elif "oa_private" == dataset_name:
            train = OAPrivate(split="train", sep_token=tokenizer.sep_token)
            eval = OAPrivate(split="val", sep_token=tokenizer.sep_token)
            train_datasets.append(train)
            evals["oa_private"] = eval

    train = ConcatDataset(train_datasets)
    return train, evals
