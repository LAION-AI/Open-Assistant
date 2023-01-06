from pathlib import Path

import yaml
from custom_datasets import QA_SPECIAL_TOKENS, get_one_dataset
from custom_datasets.dialogue_collator import DialogueDataCollator
from losses import CrossEntropyLoss
from sklearn.model_selection import train_test_split
from torch.utils.data import ConcatDataset, Subset
from transformers import AutoModelForCausalLM, AutoTokenizer


def get_tokenizer(conf):
    tokenizer = AutoTokenizer.from_pretrained(conf.model_name, cache_dir=conf.cache_dir)

    if "galactica" in conf.model_name:
        tokenizer.add_special_tokens({"pad_token": "<pad>", "eos_token": "</s>"})
    elif "GPT-JT" in conf.model_name:
        tokenizer.add_special_tokens({"pad_token": tokenizer.eos_token, "sep_token": "<|extratoken_100|>"})
    elif "codegen" in conf.model_name:
        tokenizer.add_special_tokens({"pad_token": "<|endoftext|>", "sep_token": "<|endoftext|>"})

    additional_special_tokens = (
        []
        if "additional_special_tokens" not in tokenizer.special_tokens_map
        else tokenizer.special_tokens_map["additional_special_tokens"]
    )
    additional_special_tokens = list(set(additional_special_tokens + list(QA_SPECIAL_TOKENS.values())))

    tokenizer.add_special_tokens({"additional_special_tokens": additional_special_tokens})

    return tokenizer


def get_model(conf, tokenizer):

    model = AutoModelForCausalLM.from_pretrained(conf.model_name, cache_dir=conf.cache_dir)

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


def get_loss(loss):
    if loss == "CrossEntropyLoss":
        return CrossEntropyLoss()
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


def freeze_top_n_layers(model, target_layers):
    # its possible we can simply detect which module is a ModuleList
    # and simply freeze the module without doing string parsing
    for name, param in model.named_parameters():
        if "embed" in name:
            param.requires_grad = False
        elif ".layer" in name or ".h." in name:
            tokens = name.split(".")
            layer_ = None
            for token in tokens:
                if token.isdigit():
                    layer_ = int(token)
                    break

            if layer_ is not None and layer_ < target_layers:
                # print('freeze ', layer_, name)
                param.requires_grad = False
    return model


if __name__ == "__main__":
    from transformers import AutoModelForSequenceClassification

    model = AutoModelForSequenceClassification.from_pretrained("bigscience/bloomz-560m")
    freeze_top_n_layers(model, 10)
    print(model.state_dict().keys())
