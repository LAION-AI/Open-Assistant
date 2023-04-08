import argparse
import math
import os
import random
from argparse import Namespace

import numpy as np
import torch
import transformers
import tritonclient.grpc as client_util
import trlx
from custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pairs
from models.reward_model import GPTNeoXRewardModel
from tritonclient.utils import np_to_triton_dtype
from trlx.data.configs import TRLConfig

# flake8: noqa
from utils.ppo_utils import CustomPPOTrainer
from utils.utils import _strtobool, get_dataset, get_model, init_rng, prepare_tensor, read_yamls


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


# Taken from https://github.com/CarperAI/trlx/blob/b7db6f9e74c7d8dc719255b27968d2994836957a/examples/hh/ppo_hh.py#L114
def create_reward_fn(rank_config):  # noqa:  C901
    triton_host = os.environ.get("TRITON_HOST_RM")
    assert triton_host is not None, "Specify reward mode in the TRITON_HOST environmental variable"

    triton_url, triton_model = triton_host.split("/")
    client = client_util.InferenceServerClient(url=triton_url, verbose=False)

    rank_tokenizer = transformers.AutoTokenizer.from_pretrained(rank_config.model_name, cache_dir=rank_config.cache_dir)

    def reward_fn(samples, prompts, outputs):
        if len(samples) == 0:
            return []

        inputs = rank_tokenizer(samples, return_tensors="np", padding=True)

        mbs = rank_config.batch_size
        out = []
        for i in range(math.ceil(len(samples) / mbs)):
            batch_ixs = slice(i * mbs, (i + 1) * mbs)

            # We specififed int32 as types for a triton client
            result = client.infer(
                triton_model,
                [
                    prepare_tensor("input_ids", inputs.input_ids[batch_ixs].astype(np.int32)),
                    prepare_tensor("attention_mask", inputs.attention_mask[batch_ixs].astype(np.int32)),
                ],
            )

            rewards = result.as_numpy("rewards")

            out.extend(rewards)

        return out

    return reward_fn


if __name__ == "__main__":
    training_conf = argument_parsing()

    init_rng(training_conf)

    rank_config = Namespace(**training_conf.rank_config)
    eos_token = transformers.AutoTokenizer.from_pretrained(
        rank_config.model_name, cache_dir=rank_config.cache_dir
    ).eos_token

    # Load pretrained SFT model
    sft_config = Namespace(**training_conf.sft_config)

    # override model_name to be the same as sft_model
    trlx_config = TRLConfig.load_yaml("configs/ppo_config.yaml")
    trlx_config.sft_config = sft_config

    train, eval_dict = get_dataset(training_conf, mode="rl")

    # take the dataset as the eval prompt generation dataset
    eval = eval_dict["oasst_export"] if "oasst_export" in eval_dict else eval_dict[next(iter(eval_dict))]

    # trlx requires training data to be a list of prompts
    # first element of each sample is the context and the prompt
    prompts, eval_prompts = tuple(
        map(
            lambda x: ["".join(format_pairs(x[i][0], eos_token, add_initial_reply_token=True)) for i in range(len(x))],
            (train, eval),
        )
    )

    ## Override first eval prompts just for visualization
    eval_prompts = [
        "".join(format_pairs(["Can you tell me about GLaDOS?"], eos_token, add_initial_reply_token=True)),
        "".join(format_pairs(["What is the chemical symbol for gold?"], eos_token, add_initial_reply_token=True)),
        "".join(
            format_pairs(
                ["If you were the President of the United States, what would you do?"],
                eos_token,
                add_initial_reply_token=True,
            )
        ),
    ] + eval_prompts

    random.shuffle(prompts)
    # Sanity Check for prompts to make sure it's loading properly
    with open(r"output.txt", "w") as fp:
        for item in eval_prompts:
            # write each item on a new line
            fp.write("Prompt For RL: %s\n" % item)
    print("Done")

    trlx_config.tokenizer.tokenizer_path = sft_config.model_name
    trlx_config.model.model_path = sft_config.model_name
    trlx_config.train.batch_size = int(training_conf.batch_size)
    trlx_config.method.chunk_size = int(training_conf.chunk_size)
    trlx_config.method.num_rollouts = int(training_conf.num_rollouts)
    trlx_config.train.total_steps = int(training_conf.total_steps)

    trainer = trlx.train(
        sft_config.model_name,
        reward_fn=create_reward_fn(rank_config),
        prompts=prompts,
        eval_prompts=eval_prompts,
        config=trlx_config,
        stop_sequences=[eos_token],
    )

    training_conf.output_dir = training_conf.output_dir if training_conf.output_dir else training_conf.model_name

    trainer.save_pretrained(training_conf.output_dir)
