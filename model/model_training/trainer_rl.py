import argparse
import random

import torch
import transformers
import trlx
from custom_datasets.formatting import QA_SPECIAL_TOKENS
from models import get_specific_model
from trlx.data.configs import TRLConfig
from utils import _strtobool, get_dataset, read_yamls


def argument_parsing(notebook=False, notebook_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--local_rank", type=int, default=-1)

    if notebook:
        args, remaining = parser.parse_known_args(notebook_args)
    else:
        args, remaining = parser.parse_known_args()

    print(args)

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

    assert training_conf.rank_model != training_conf.dataset, "One of rank model or dataset must be different"

    # Load pretrained rank model

    # TODO add RankGenModel option for rankgen-t5 models
    # TODO decide on device for this model, possibly different node.
    # TODO add <load_in_8bit=True, device_map='auto', torch_dtype=torch.float16, low_cpu_mem_usage=True, offload_state_dict=True>, currently not supported from all models ...
    rank_model = transformers.AutoModelForSequenceClassification.from_pretrained(
        training_conf.rank_model,
    )
    rank_model.eval()
    rank_model.gradient_checkpointing_enable()  # reduce number of stored activations

    rank_tokenizer = transformers.AutoTokenizer.from_pretrained(training_conf.rank_model)

    # TODO sync with reward modelling team on how to do this more transparently
    @torch.no_grad()
    def rank_model_fn(samples, **kwargs):
        inputs = rank_tokenizer(samples, return_tensors="pt", padding=True)
        inputs.pop("token_type_ids", None)
        return rank_model(**inputs).logits[:, 0].detach().cpu()

    trlx_config = TRLConfig.load_yaml("configs/ppo_config.yaml")

    train, _ = get_dataset(training_conf, mode="rl")

    # trlx requires training data to be a list of prompts
    # iteratore prompts due to the randomness in the dataset generation
    prompts = [train[i] for i in range(len(train)) for _ in range(training_conf.epochs)]

    random.shuffle(prompts)

    model = get_specific_model(
        training_conf.sft_model,
        cache_dir=training_conf.cache_dir,
        quantization=training_conf.quantization,
        seq2seqmodel=training_conf.seq2seqmodel,
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(training_conf.sft_model)

    trlx_config.tokenizer.tokenizer_path = training_conf.sft_model
    trlx_config.model.model_path = training_conf.sft_model
    trlx_config.train.batch_size = training_conf.batch_size

    trainer = trlx.train(
        training_conf.sft_model,
        reward_fn=rank_model_fn,
        prompts=prompts,
        config=trlx_config,
        stop_sequences=[tokenizer.eos_token, QA_SPECIAL_TOKENS["Question"]],
    )

    training_conf.output_dir = training_conf.output_dir if training_conf.output_dir else training_conf.model_name

    trainer.save_pretrained(training_conf.output_dir)
