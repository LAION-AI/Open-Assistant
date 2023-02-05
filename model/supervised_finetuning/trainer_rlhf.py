import os
import torch
import trlx
import transformers
import argparse
from utils import read_yamls, _strtobool
from trlx.data.configs import TRLConfig


def argument_parsing(notebook=False, notebook_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--local_rank", type=int, default=-1)
    parser.add_argument("--wandb-entity", type=str, default="open-assistant")

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

    conf["wandb_entity"] = args.wandb_entity
    conf["local_rank"] = args.local_rank

    # Override config from command-line
    parser = argparse.ArgumentParser()
    for key, value in conf.items():
        type_ = type(value) if value is not None else str
        if type_ == bool:
            type_ = _strtobool
        parser.add_argument(f"--{key}", type=type_, default=value)

    return parser.parse_args(remaining)


def test_dataset():
    import sqlite3
    from urllib.request import urlretrieve

    url = "https://raw.githubusercontent.com/JD-P/simulacra-aesthetic-captions/main/sac_public_2022_06_29.sqlite"
    dbpath = "sac_public_2022_06_29.sqlite"

    if not os.path.exists(dbpath):
        print(f"fetching {dbpath}")
        urlretrieve(url, dbpath)

    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute(
        "SELECT prompt, rating FROM ratings "
        "JOIN images ON images.id=ratings.iid "
        "JOIN generations ON images.gid=generations.id "
        "WHERE rating IS NOT NULL;"
    )

    prompts, ratings = tuple(map(list, zip(*c.fetchall())))

    return prompts, ratings


if __name__ == "__main__":
    training_conf = argument_parsing()

    assert training_conf.rank_model != training_conf.dataset, "One of rank model or dataset must be different"

    if training_conf.rank_model:
        # Load pretrained rank model

        # TODO add RankGenModel option for rankgen-t5 models
        # TODO decide on device for this model
        # TODO add <load_in_8bit=True, device_map='auto', torch_dtype=torch.float16, low_cpu_mem_usage=True, offload_state_dict=True>, currently not supported from all models ...
        rank_model = transformers.AutoModelForSequenceClassification.from_pretrained(
            training_conf.rank_model,
        )
        rank_model.eval()
        rank_model.gradient_checkpointing_enable()  # reduce number of stored activations

        tokenizer = transformers.AutoTokenizer.from_pretrained(training_conf.rank_model)

        @torch.no_grad()
        def rank_model_fn(questions, answers, **kwargs):
            inputs = tokenizer(questions, answers, return_tensors="pt")
            return rank_model(**inputs).logits[:, 0].detach().cpu()

        reward_fn = lambda questions, answers, **kwargs: rank_model_fn(questions, answers, **kwargs)
        trlx_config = TRLConfig.load_yaml("configs/ppo_config.yml")
    else:
        reward_fn = None

    if training_conf.dataset == "test_dataset":
        # Load dataset
        train_dataset = test_dataset()
        trlx_config = TRLConfig.load_yaml("configs/ilql_config.yml")
    else:
        train_dataset = None

    if training_conf.eval_prompts == "test_promps":
        eval_prompts = ["Hatsune Miku, Red Dress"] * 64

    trlx_config.tokenizer.tokenizer_path = training_conf.model_name
    trlx_config.train.batch_size = training_conf.batch_size

    trainer = trlx.train(
        training_conf.model_name,
        reward_fn=reward_fn,
        dataset=train_dataset,
        config=trlx_config,
        eval_prompts=eval_prompts,
    )
