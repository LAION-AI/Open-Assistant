import argparse
import copy
import math
import random
from distutils.util import strtobool
from pathlib import Path
from typing import List, NamedTuple

import evaluate
import torch
import transformers
import yaml
from model_training.custom_datasets import get_one_dataset
from model_training.custom_datasets.formatting import QA_SPECIAL_TOKENS
from model_training.models import freeze_top_n_layers, get_specific_model
from model_training.models.patching import patch_model
from model_training.models.prefix_llama import LlamaForCausalLM
from model_training.models.reward_model import GPTNeoXRewardModel
from sklearn.model_selection import train_test_split
from tokenizers import pre_tokenizers
from torch.utils.data import ConcatDataset, Dataset, Subset
from torch.utils.data.distributed import DistributedSampler

from .losses import CrossEntropyLoss, PolyLoss, RMCLSLoss, RMLoss


def _strtobool(x):
    return bool(strtobool(x))


def init_rng(conf: argparse.Namespace) -> None:
    seed = conf.rng_seed
    if seed is not None:
        print(f"RNG seed: {seed}")
        transformers.set_seed(seed)


class PerDatasetSampler(DistributedSampler):
    """Sampler which returns a fixed number of samples per dataset, per epoch.

    Example:

    Dataset 1 has 10,000 examples and we want 200 per epoch
    Dataset 2 has 500 examples and we want all 500 per epoch

    Epoch size will be 700 and every epoch we'll sample a different
    200 from dataset 1.

    Parameters
    ----------
    dataset_sizes : List[int]
        A list with the size of each dataset.
    dataset_size_per_epoch : List[int]
        How many examples to get from each dataset per epoch.

    Note: dataset_sizes & dataset_size_per_epoch must be in the same order.
    Further the examples in the underlying torch.utils.data.Dataset
    must per ordered as dataset_1, dataset_2, ..., dataset_n. This is fine
    if we concatenate a bunch of datasets together
    e.g. using torch.utils.data.ConcatDataset which is current behaviour.
    """

    def __init__(
        self,
        dataset_sizes: List[int],
        dataset_size_per_epoch: List[int],
        rank: int = None,
        world_size: int = None,
        shuffle: bool = True,
        seed: int = 0,
        samples_length: List[int] = None,
    ):
        """
        if samples_length is not None, then the sampler
        will order the samples by dataset length
        with some variability across epochs
        """
        self.dataset_sizes = dataset_sizes
        self.dataset_size_per_epoch = dataset_size_per_epoch
        self.num_datasets = len(dataset_sizes)
        self.shuffle = shuffle
        self.rank = rank
        self.world_size = world_size
        self.epoch = 0

        if world_size == 1:
            self.rank = 0

        self.num_samples = sum(dataset_size_per_epoch)
        self.seed = seed
        self.samples_length = samples_length

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch

    def __len__(self) -> int:
        return self.num_samples // self.world_size

    def __iter__(self):
        epoch_idx = []
        n = 0

        random.seed(self.epoch + self.seed)

        for i in range(self.num_datasets):
            sampled_idx = random.sample(range(n, self.dataset_sizes[i] + n), self.dataset_size_per_epoch[i])
            n += self.dataset_sizes[i]
            epoch_idx.extend(sampled_idx)

        if self.samples_length is not None:
            # sort by samples length and in case of ties randomize
            epoch_idx = sorted(epoch_idx, key=lambda x: (self.samples_length[x], random.random()))

            if self.shuffle:
                # do some minor shuffling to avoid repeating the same order
                # but not too much to avoid too much padding
                # quasi random basically
                for i in range(0, len(epoch_idx), 200):  # this should be batch_size dependent
                    random.shuffle(epoch_idx[i : i + 200])
        else:
            if self.shuffle:
                random.shuffle(epoch_idx)

        # split epoch_idx in world_size chunks
        epoch_idx = epoch_idx[self.rank : self.num_samples : self.world_size]

        return iter(epoch_idx)

    @classmethod
    def build_sampler_from_config(cls, training_conf, datasets: List[Dataset], verbose: bool = False, **kwargs):
        dataset_sizes = [len(x) for x in datasets]
        fractions = get_dataset_fractions(training_conf.datasets, dataset_sizes, verbose)
        dataset_size_per_epoch = [int(size * frac) for size, frac in zip(dataset_sizes, fractions)]
        seed = training_conf.rng_seed
        return cls(dataset_sizes=dataset_sizes, dataset_size_per_epoch=dataset_size_per_epoch, seed=seed, **kwargs)


def get_dataset_fractions(conf, dataset_sizes: List[int], verbose: bool = False):
    """Calculate fraction of each dataset to use per epoch when sub-sampling"""

    if verbose:
        print("Creating sampler for datasets:")

    fractions = []
    for i, data_config in enumerate(conf):
        dataset_name, _ = get_dataset_name_and_kwargs_from_data_config(data_config)
        if isinstance(data_config, dict):
            if "fraction" in data_config[dataset_name]:
                if data_config[dataset_name]["fraction"] <= 0:
                    raise ValueError("Please specify fraction as a value between 0 < fraction <= 1")
                fractions.append(min(1, data_config[dataset_name]["fraction"]))
            elif "size" in data_config[dataset_name]:
                if data_config[dataset_name]["size"] > dataset_sizes[i]:
                    raise ValueError(f"Please specify a size smaller than number of examples: {dataset_sizes[i]:,.0f}")
                fractions.append(data_config[dataset_name]["size"] / dataset_sizes[i])
            else:
                fractions.append(1)
        else:
            fractions.append(1)

        if verbose:
            print(f"{dataset_name}: {fractions[-1]:.2%} ({int(dataset_sizes[i]*fractions[-1])})")
    return fractions


class SpecialTokens(NamedTuple):
    pad_token: str = ""
    eos_token: str = ""
    sep_token: str = ""


class TokenizerConfig(NamedTuple):
    special_tokens: SpecialTokens = {}


TOKENIZER_CONFIGS = {
    "galactica": TokenizerConfig(special_tokens=SpecialTokens("<pad>", "</s>")),
    "GPT-JT": TokenizerConfig(special_tokens=SpecialTokens(sep_token="<|extratoken_100|>")),
    "codegen": TokenizerConfig(special_tokens=SpecialTokens("<|endoftext|>", sep_token="<|endoftext|>")),
    "pythia": TokenizerConfig(special_tokens=SpecialTokens("<|padding|>", "<|endoftext|>", "<|endoftext|>")),
    "gpt-neox": TokenizerConfig(special_tokens=SpecialTokens("<|padding|>", "<|endoftext|>", "<|endoftext|>")),
    "llama": TokenizerConfig(special_tokens=SpecialTokens("</s>", "</s>", sep_token="<s>")),
    "cerebras": TokenizerConfig(special_tokens=SpecialTokens("<|endoftext|>", "<|endoftext|>", "<|endoftext|>")),
    "deberta-v3": TokenizerConfig(special_tokens=SpecialTokens("[PAD]", "[SEP]", sep_token="[CLS]")),
    "bloom": TokenizerConfig(special_tokens=SpecialTokens("<pad>", "</s>", "<s>")),
    "electra": TokenizerConfig(special_tokens=SpecialTokens("[PAD]", "[SEP]", sep_token="[CLS]")),
    "falcon": TokenizerConfig(
        special_tokens=SpecialTokens("<|endoftext|>", "<|endoftext|>", sep_token="<|endoftext|>")
    ),
    "LLongMA": TokenizerConfig(special_tokens=SpecialTokens("</s>", "</s>", sep_token="<s>")),
}


def match_tokenizer_name(model_name: str) -> TokenizerConfig:
    """
    Match a partial model name to a tokenizer configuration
    i.e. model_name `Salesforce/codegen-2B-multi` has config name `codegen`
    """
    tokenizer_config_matches = [config for name, config in TOKENIZER_CONFIGS.items() if name in model_name]
    if not tokenizer_config_matches:
        raise ValueError(f"Cannot find any tokeniser configuration to match {model_name=}")
    elif 1 < len(tokenizer_config_matches):
        raise ValueError(f"Found multiple tokeniser configuration matches for {model_name=}")
    else:
        return tokenizer_config_matches[0]


def get_tokenizer(conf) -> transformers.AutoTokenizer:
    tokenizer_name = conf.model_name

    if "cerebras" in conf.model_name:
        # Only 13B has a tokenizer available on HF
        tokenizer_name = "cerebras/Cerebras-GPT-13B"

    tokenizer = transformers.AutoTokenizer.from_pretrained(tokenizer_name, cache_dir=conf.cache_dir)

    tokenizer_config = match_tokenizer_name(conf.model_name)

    if hasattr(conf, "per_digit_tokens") and conf.per_digit_tokens:
        tokenizer._tokenizer.pre_processor = pre_tokenizers.Digits(True)

    if tokenizer_config.special_tokens:
        if "GPT-JT" in conf.model_name:
            tokenizer_config.special_tokens.pad_token = tokenizer.eos_token
        # SpecialTokens : latest in 4.25, 4.26
        tokenizer.add_special_tokens(
            {
                "pad_token": tokenizer_config.special_tokens.pad_token,
                "eos_token": tokenizer_config.special_tokens.eos_token,
                "sep_token": tokenizer_config.special_tokens.sep_token,
            }
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


def get_model(conf, tokenizer, pad_vocab_size_to_multiple_of=16, check_freeze_layer=True):
    dtype = torch.float32
    if conf.dtype in ["fp16", "float16"]:
        dtype = torch.float16
    elif conf.dtype in ["bf16", "bfloat16"]:
        dtype = torch.bfloat16

    if conf.is_reward_model:
        if "pythia" in conf.model_name:
            model = GPTNeoXRewardModel.from_pretrained(conf.model_name, cache_dir=conf.cache_dir, torch_dtype=dtype)

            if conf.pooling:
                assert conf.pooling in ("mean", "last"), f"invalid pooling configuration '{conf.pooling}'"
                model.config.pooling = conf.pooling
        else:
            model = transformers.AutoModelForSequenceClassification.from_pretrained(
                conf.model_name, cache_dir=conf.cache_dir, num_labels=1, torch_dtype=dtype
            )
    if not conf.is_reward_model:
        if conf.peft_type is not None and conf.peft_type == "prefix-tuning" and "llama" in conf.model_name:
            model = LlamaForCausalLM.from_pretrained(conf.model_name, cache_dir=conf.cache_dir, torch_dtype=dtype)
        else:
            model = get_specific_model(
                conf.model_name,
                cache_dir=conf.cache_dir,
                quantization=conf.quantization,
                seq2seqmodel=conf.seq2seqmodel,
                without_head=conf.is_reward_model,
                torch_dtype=dtype,
            )

        n_embs = model.get_input_embeddings().num_embeddings
        if len(tokenizer) != n_embs or pad_vocab_size_to_multiple_of:
            p = pad_vocab_size_to_multiple_of
            target_size = len(tokenizer) if not p else math.ceil(len(tokenizer) / p) * p
            print("Resizing embeddings to", target_size)
            model.resize_token_embeddings(target_size)

        new_n_embs = model.get_input_embeddings().num_embeddings
        if new_n_embs != n_embs and check_freeze_layer:
            assert not conf.freeze_layer, "Cannot change the number of embeddings if the model is frozen."

        if conf.freeze_layer:
            model = freeze_top_n_layers(model, conf.freeze_layer)

    model_parameters = filter(lambda p: p.requires_grad, model.parameters())
    params = sum([p.numel() for p in model_parameters])
    print("Number of trainable parameters: {}M".format(int(params / 1e6)))

    patch_model(
        model,
        resid_pdrop=conf.residual_dropout,
        flash_attention=conf.use_flash_attention,
        residual_dropout_lima=conf.residual_dropout_lima,
    )

    return model


def get_dataset_name_and_kwargs_from_data_config(data_config):
    if isinstance(data_config, dict):
        name = list(data_config.keys())[0]

        # first copy the dict, then remove the size and fraction
        kwargs = copy.deepcopy(data_config[name])

        kwargs.pop("fraction", None)
        kwargs.pop("size", None)
        return name, kwargs
    else:
        return data_config, {}


def get_dataset(
    conf,
    mode: str = "sft",
) -> tuple[ConcatDataset, dict[str, Subset]]:
    train_datasets, evals = [], {}

    for data_config in conf.datasets + conf.datasets_extra:
        dataset_name, kwargs = get_dataset_name_and_kwargs_from_data_config(data_config)
        train, val = get_one_dataset(conf, dataset_name, mode=mode, **kwargs)
        train_datasets.append(train)

        if val is not None:
            evals[dataset_name] = Subset(val, list(range(min(len(val), conf.eval_size)))) if conf.eval_size else val

    train = ConcatDataset(train_datasets)

    return train, evals


def get_loss(loss, poly_eps: float = 1.0, score_l2_reg: float = 0.001):
    if loss == "CrossEntropyLoss":
        return CrossEntropyLoss()
    elif loss == "Poly":
        return PolyLoss(epsilon=poly_eps)
    elif loss == "RMLoss":
        return RMLoss(beta=score_l2_reg)
    elif loss == "RMCLSLoss":
        return RMCLSLoss()
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
    if val_split == 0:
        return dataset, None

    train_idx, val_idx = train_test_split(
        list(range(len(dataset))), test_size=val_split, random_state=666, shuffle=True
    )
    return Subset(dataset, train_idx), Subset(dataset, val_idx)


def process_output(output: str, method: str = "v2", bot_name: str = "Joi") -> str:
    if method == "v2":
        answer = output.split(QA_SPECIAL_TOKENS["Answer"])[-1]
        answer = answer.split("</s>")[0].replace("<|endoftext|>", "").lstrip().split(QA_SPECIAL_TOKENS["Answer"])[0]
    else:
        answer = output.split("\n\n{}:".format(bot_name))[-1]
        answer = answer.split("</s>")[0].replace("<|endoftext|>", "").lstrip().split("\n\n{}:".format(bot_name))[0]
    return answer


def merge_dicts(default: dict, config: dict):
    """
    merge default dict with config dict to override params
    """
    for k, v in default.items():
        if k not in config.keys():
            config.update({k: v})

    return config


def get_all_linear_layers(model):
    cls = torch.nn.Linear

    modules = {name.split(".")[-1] for name, module in model.named_modules() if isinstance(module, cls)}
    if "lm_head" in modules:
        modules.remove("lm_head")

    return list(modules)
