import argparse
import random
from argparse import Namespace

import torch
import transformers
import trlx
from custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pairs
from models.reward_model import GPTNeoXRewardModel
from trlx.data.configs import TRLConfig

# flake8: noqa
from utils.ppo_trainer import CustomPPOTrainer
from utils.utils import _strtobool, get_dataset, get_model, read_yamls


def argument_parsing(notebook=False, notebook_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--local_rank", type=int, default=-1)
    parser.add_argument("--wandb-entity", type=str, default="open-assistant")

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

    # Load pretrained rank model
    rank_config = Namespace(**training_conf.rank_config)
    rank_tokenizer = transformers.AutoTokenizer.from_pretrained(rank_config.model_name)

    rank_model = get_model(rank_config, rank_tokenizer)
    rank_model.eval()

    # TODO sync with reward modelling team on how to do this more transparently
    @torch.no_grad()
    def rank_model_fn(samples, **kwargs):
        # Here it is better to truncate to the left but model is is inference
        # so we can get away without truncating at all
        if len(samples) == 0:
            return []

        inputs = rank_tokenizer(samples, return_tensors="pt", padding=True)

        if "token_type_ids" in inputs:
            del inputs["token_type_ids"]

        return rank_model(**inputs).logits.detach().cpu()[:, 0]

    sft_config = Namespace(**training_conf.sft_config)
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        sft_config.model_name, padding_side="left" if not sft_config.seq2seqmodel else "right"
    )
    assert rank_tokenizer.eos_token == tokenizer.eos_token

    # override model_name to be the same as sft_model
    model = get_model(sft_config, tokenizer)

    trlx_config = TRLConfig.load_yaml("configs/ppo_config.yaml")

    train, eval_dict = get_dataset(training_conf, mode="rl")

    # take the dataset as the eval prompt generation dataset
    eval = eval_dict["oasst_export"] if "oasst_export" in eval_dict else eval_dict[next(iter(eval_dict))]

    # trlx requires training data to be a list of prompts
    # first element of each sample is the context and the prompt
    prompts, eval_prompts = tuple(
        map(
            lambda x: [
                "".join(format_pairs(x[i][0], rank_tokenizer.eos_token, add_initial_reply_token=True))
                for i in range(len(x))
            ],
            (train, eval),
        )
    )

    random.shuffle(prompts)

    trlx_config.tokenizer.tokenizer_path = sft_config.model_name
    trlx_config.model.model_path = sft_config.model_name
    trlx_config.train.batch_size = training_conf.batch_size

    trainer = trlx.train(
        sft_config.model_name,
        reward_fn=rank_model_fn,
        prompts=prompts,
        eval_prompts=eval_prompts[:200],
        config=trlx_config,
        stop_sequences=[tokenizer.eos_token, QA_SPECIAL_TOKENS["Question"]],
    )

    training_conf.output_dir = training_conf.output_dir if training_conf.output_dir else training_conf.model_name

    trainer.save_pretrained(training_conf.output_dir)
