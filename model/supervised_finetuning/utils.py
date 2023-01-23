# from functools import partial
from pathlib import Path

import evaluate

# import nltk
# import numpy as np
import transformers
import yaml
from custom_datasets import get_one_dataset
from custom_datasets.dialogue_collator import DialogueDataCollator
from custom_datasets.qa_datasets import QA_SPECIAL_TOKENS
from losses import CrossEntropyLoss, PolyLoss
from models import freeze_top_n_layers, get_specific_model
from sklearn.model_selection import train_test_split
from torch.utils.data import ConcatDataset, Subset


def get_tokenizer(conf):
    tokenizer = transformers.AutoTokenizer.from_pretrained(conf.model_name, cache_dir=conf.cache_dir)

    if "galactica" in conf.model_name:
        tokenizer.add_special_tokens({"pad_token": "<pad>", "eos_token": "</s>"})
    elif "GPT-JT" in conf.model_name:
        tokenizer.add_special_tokens({"pad_token": tokenizer.eos_token, "sep_token": "<|extratoken_100|>"})
    elif "codegen" in conf.model_name:
        tokenizer.add_special_tokens({"pad_token": "<|endoftext|>", "sep_token": "<|endoftext|>"})
    elif "pythia" in conf.model_name:
        tokenizer.add_special_tokens(
            {"pad_token": "<|padding|>", "sep_token": "<|endoftext|>", "eos_token": "<|endoftext|>"}
        )

    additional_special_tokens = (
        []
        if "additional_special_tokens" not in tokenizer.special_tokens_map
        else tokenizer.special_tokens_map["additional_special_tokens"]
    )
    additional_special_tokens = list(set(additional_special_tokens + list(QA_SPECIAL_TOKENS.values())))

    tokenizer.add_special_tokens({"additional_special_tokens": additional_special_tokens})

    return tokenizer


def default_preprocess(eval_pred, ignote_negative_labels=True):
    preds, labels = eval_pred.predictions, eval_pred.label_ids

    if not ignote_negative_labels:
        return preds, labels

    mask = labels > 0
    return preds[mask], labels[mask]


# placeholder for now
def preprocess_qa(eval_pred):
    return (eval_pred.predictions, eval_pred.label_ids)


# def postprocess_summarization(preds, labels):
#     preds = [pred.strip() for pred in preds]
#     labels = [label.strip() for label in labels]

#     preds = ["\n".join(nltk.sent_tokenize(pred)) for pred in preds]
#     labels = ["\n".join(nltk.sent_tokenize(label)) for label in labels]

#     return preds, labels


# def preprocess_summarization(eval_pred, tokenizer, ignore_pad_token_for_loss=True):
#     preds, labels = eval_pred
#     decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
#     if ignore_pad_token_for_loss:
#         labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
#     decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

#     decoded_preds, decoded_labels = postprocess_summarization(decoded_preds, decoded_labels)
#     return decoded_preds, decoded_labels


def get_metrics(conf, tokenizer):
    # the reason behind using a list is that we might want to extend the list of our
    # metrics in the future for more thorough evaluation
    metrics, preprocess_fns = [evaluate.load("accuracy")], [default_preprocess]

    # if any(dataset in QA_DATASETS for dataset in conf.datasets):
    #     raise ValueError("TODO")
    #     metrics.append(evaluate.load("squad_v2"))
    #     preprocess_fns.append(preprocess_qa)
    # if any(dataset in SUMMARIZATION_DATASETS for dataset in conf.datasets):
    #     raise ValueError("TODO")
    #     metrics.append(evaluate.load("rouge"))
    #     preprocess_fns.append(
    #         partial(preprocess_summarization, tokenizer, ignore_pad_token_for_loss=conf.ignore_pad_token_for_loss)
    #     )

    return metrics, preprocess_fns


def get_model(conf, tokenizer):
    model = get_specific_model(conf.model_name, conf.cache_dir, conf.quantization, conf.seq2seqmodel)

    if len(tokenizer) != model.get_input_embeddings().num_embeddings:
        assert not conf.freeze_layer, "Cannot change the number of embeddings if the model is frozen."

    model.resize_token_embeddings(len(tokenizer))

    if conf.freeze_layer:
        model = freeze_top_n_layers(model, conf.freeze_layer)

    model_parameters = filter(lambda p: p.requires_grad, model.parameters())
    params = sum([p.numel() for p in model_parameters])
    print("Number of trainable parameters: {}M".format(int(params / 1e6)))

    return model


def get_dataset(conf, tokenizer):
    train_datasets, evals = [], {}

    for dataset_name in conf.datasets:
        train, val = get_one_dataset(conf, dataset_name)
        train_datasets.append(train)
        evals[dataset_name] = Subset(val, list(range(min(len(val), conf.eval_size)))) if conf.eval_size else val

    train = ConcatDataset(train_datasets)

    collate_fn = DialogueDataCollator(tokenizer, max_length=conf.max_length)

    return train, evals, collate_fn


def get_loss(loss, poly_eps):
    if loss == "CrossEntropyLoss":
        return CrossEntropyLoss()
    elif loss == "Poly":
        return PolyLoss(epsilon=poly_eps)
    else:
        raise ValueError(f"Loss {loss} not supported")


def read_yamls(dir):
    conf = {}
    no_conf = True

    for config_file in Path(dir).glob("**/*.yaml"):
        no_conf = False
        with config_file.open("r") as f:
            conf.update(yaml.safe_load(f))

    if no_conf:
        print(f"WARNING: No yaml files found in {dir}")

    return conf


def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)
