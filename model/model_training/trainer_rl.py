import argparse
import math
import os
import random
from argparse import Namespace
from typing import Sequence

import numpy as np
import torch
import transformers
import tritonclient.grpc as client_util
import trlx
from model_training.custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pairs
from model_training.models import get_specific_model
from model_training.utils.utils import _strtobool, get_dataset, init_rng, read_yamls
from tritonclient.utils import np_to_triton_dtype
from trlx.data.configs import TRLConfig

# flake8: noqa
from utils.ppo_utils import CustomPPOTrainer
from utils.utils import _strtobool, get_dataset, get_model, init_rng, read_yamls
from utils.utils_rl import prepare_tensor


def argument_parsing(notebook: bool = False, notebook_args: Sequence[str] | None = None, **kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--local_rank", type=int, default=-1)
    parser.add_argument("--wandb-entity", type=str, default="open-assistant")
    parser.add_argument("--rng_seed", type=int, help="rng seed")

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
    if args.rng_seed is not None:
        conf["rng_seed"] = args.rng_seed

    # Override config from command-line
    parser = argparse.ArgumentParser()

    for key, value in kwargs.items():
        type_ = type(value) if value is not None else str
        parser.add_argument(f"--{key}", type=type_, default=value)

    for key, value in conf.items():
        type_ = type(value) if value is not None else str
        if type_ == bool:
            type_ = _strtobool
        parser.add_argument(f"--{key}", type=type_, default=value)

    return parser.parse_args(remaining)


# Taken from https://github.com/CarperAI/trlx/blob/b7db6f9e74c7d8dc719255b27968d2994836957a/examples/hh/ppo_hh.py#L114
def create_reward_fn(rank_config, sft_config):  # noqa:  C901
    triton_host = os.environ.get("TRITON_HOST_RM")
    assert triton_host is not None, "Specify reward model in the TRITON_HOST_RM environmental variable"

    triton_url, triton_model = triton_host.split("/")
    client = client_util.InferenceServerClient(url=triton_url, verbose=False)

    rank_tokenizer = transformers.AutoTokenizer.from_pretrained(rank_config.model_name, cache_dir=rank_config.cache_dir)
    sft_tokenizer = transformers.AutoTokenizer.from_pretrained(sft_config.model_name, cache_dir=sft_config.cache_dir)

    def reward_fn(samples, prompts, outputs):
        if len(samples) == 0:
            return []

        # hack to allo for different tokenizers with different eos tokens ... rest of the
        samples = [x.replace(sft_tokenizer.eos_token, rank_tokenizer.eos_token) for x in samples]
        samples = [x.replace(sft_tokenizer.pad_token, rank_tokenizer.pad_token) for x in samples]

        inputs = rank_tokenizer(samples, return_tensors="np", padding=True)

        mbs = rank_config.batch_size
        out = []
        for i in range(math.ceil(len(samples) / mbs)):
            batch_ixs = slice(i * mbs, (i + 1) * mbs)

            # We specified int32 as types for a triton client
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


def main():
    training_conf = argument_parsing()
    rank_config = Namespace(**training_conf.rank_config)
    sft_config = Namespace(**training_conf.sft_config)

    triton_host_rm = os.getenv("TRITON_HOST_RM", training_conf.triton_host_rm)
    triton_host_sft = os.getenv("TRITON_HOST_REF", training_conf.triton_host_sft)
    os.environ["TRITON_HOST_RM"] = triton_host_rm
    os.environ["TRITON_HOST_REF"] = triton_host_sft

    init_rng(training_conf)

    eos_token = transformers.AutoTokenizer.from_pretrained(
        sft_config.model_name, cache_dir=sft_config.cache_dir
    ).eos_token

    # Load pretrained SFT model

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

    if training_conf.num_eval_prompts is not None and training_conf.num_eval_prompts > 0:
        eval_prompts = eval_prompts[: training_conf.num_eval_prompts]

    random.shuffle(prompts)
    # Sanity Check for prompts to make sure it's loading properly
    with open(r"output.txt", "w") as fp:
        for item in eval_prompts:
            # write each item on a new line
            fp.write("Prompt For RL: %s\n" % item)

    trlx_config.tokenizer.tokenizer_path = sft_config.model_name
    trlx_config.model.model_path = sft_config.model_name
    trlx_config.train.batch_size = int(training_conf.batch_size)
    trlx_config.method.chunk_size = int(training_conf.chunk_size)
    trlx_config.method.num_rollouts = int(training_conf.num_rollouts)
    trlx_config.train.total_steps = int(training_conf.total_steps)

    if training_conf.debug:
        print("Continuing in debug mode")
        prompts = prompts[:10]
        eval_prompts = eval_prompts[:10]
        trlx_config.method.num_rollouts = 1
        # trlx_config.method.gen_kwargs['max_new_tokens'] = 12
        # trlx_config.train.seq_length = 48

    trainer = trlx.train(
        sft_config.model_name,
        reward_fn=create_reward_fn(rank_config, sft_config),
        prompts=prompts,
        eval_prompts=eval_prompts,
        config=trlx_config,
        stop_sequences=[eos_token],
    )

    training_conf.output_dir = training_conf.output_dir if training_conf.output_dir else training_conf.model_name

    trainer.save_pretrained(training_conf.output_dir)


if __name__ == "__main__":
    main()
