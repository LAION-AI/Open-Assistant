import argparse
import random

import torch
import transformers
import trlx
from custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pairs
from models.reward_model import RewardModel
from trlx.data.configs import TRLConfig
from utils import _strtobool, get_dataset, get_model, read_yamls


def argument_parsing(notebook=False, notebook_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--wandb-entity", type=str, default="open-assistant")
    # parser.add_argument("--local_rank", type=int, default=-1)

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

    # conf["local_rank"] = args.local_rank

    # Override config from command-line
    parser = argparse.ArgumentParser()
    for key, value in conf.items():
        type_ = type(value) if value is not None else str
        if type_ == bool:
            type_ = _strtobool
        parser.add_argument(f"--{key}", type=type_, default=value)
        parser.add_argument(f"--no-{key}", dest=key, action="store_const", const=None)

    return parser.parse_args(remaining)


if __name__ == "__main__":
    training_conf = argument_parsing()

    # Load pretrained rank model
    # TODO make sure model is initialized correctly.
    rank_model = RewardModel.from_pretrained(
        training_conf.rank_model,
    )
    rank_model.eval()

    rank_tokenizer = transformers.AutoTokenizer.from_pretrained(training_conf.rank_model)

    @torch.no_grad()
    def rank_model_fn(samples, **kwargs):
        # Here it is better to truncate to the left but model is is inference
        # so we can get away without truncating at all
        inputs = rank_tokenizer(samples, return_tensors="pt", padding=True)

        if "token_type_ids" in inputs:
            del inputs["token_type_ids"]

        return rank_model(**inputs).detach().cpu()[:, 0]

    trlx_config = TRLConfig.load_yaml("configs/ppo_config.yaml")

    train, _ = get_dataset(training_conf, mode="rl")

    # trlx requires training data to be a list of prompts
    # first element of each sample is the context and the prompt
    prompts = [
        "".join(format_pairs(train[i][0], rank_tokenizer.eos_token, add_initial_reply_token=True))
        for i in range(len(train))
    ]

    random.shuffle(prompts)

    tokenizer = transformers.AutoTokenizer.from_pretrained(training_conf.sft_model)

    # the two tokenizers ideally should be the same ...
    rank_tokenizer.eos_token == tokenizer.eos_token

    # override model_name to be the same as sft_model
    training_conf.model_name = training_conf.sft_model
    model = get_model(training_conf, tokenizer)

    trlx_config.tokenizer.tokenizer_path = training_conf.sft_model
    trlx_config.model.model_path = training_conf.sft_model
    trlx_config.train.batch_size = training_conf.batch_size

    print(prompts[0])

    trainer = trlx.train(
        training_conf.sft_model,
        reward_fn=rank_model_fn,
        prompts=prompts,
        config=trlx_config,
        stop_sequences=[tokenizer.eos_token, QA_SPECIAL_TOKENS["Question"]],
    )

    training_conf.output_dir = training_conf.output_dir if training_conf.output_dir else training_conf.model_name

    trainer.save_pretrained(training_conf.output_dir)
