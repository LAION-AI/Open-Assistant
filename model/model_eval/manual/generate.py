import argparse
import gzip
import json
from pathlib import Path

import pydantic
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer

QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


class SamplingConfig(pydantic.BaseModel):
    name: str
    generate_args: dict
    pre_text: str

    # for legacy models
    human_name: str = "User"
    bot_name: str = "Joi"


def load_jsonl(input_file_path: str | Path) -> list[dict | str]:
    if not isinstance(input_file_path, Path):
        input_file_path = Path(input_file_path)

    if input_file_path.suffix == ".gz":
        file_in = gzip.open(str(input_file_path), mode="tr", encoding="UTF-8")
    else:
        file_in = input_file_path.open("r", encoding="UTF-8")

    items = []

    with file_in:
        # read one message tree per line
        for line in file_in:
            obj = json.loads(line)
            items.append(obj)

    return items


def sample(prompt: str, model, tokenizer: PreTrainedTokenizer, mode: str, sampling_config: SamplingConfig):
    sc = sampling_config
    prefix = ""
    if sampling_config.pre_text:
        if mode == "v2":
            prefix = f"<prefix>{sampling_config.pre_text}</prefix>"
        else:
            prefix = sampling_config.pre_text

    if mode == "v2":
        input_text = f"{prefix}{QA_SPECIAL_TOKENS['Question']}{prompt}{QA_SPECIAL_TOKENS['Answer']}"
    else:
        input_text = f"{prefix}\n{sc.human_name}: {prompt}\n\n{sc.bot_name}: "

    inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(0)
    input_ids = inputs.input_ids
    outputs = model.generate(
        input_ids,
        **sampling_config.generate_args,
        early_stopping=True,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    return outputs


def sample_prompt_continuations(
    prompts: list[str], model, tokenizer: PreTrainedTokenizer, mode: str, sampling_configs: list[SamplingConfig]
):
    # prepare prompt
    for p in prompts:
        for sc in sampling_configs:
            outputs = sample(p, model=model, tokenizer=tokenizer, mode=mode, sampling_config=sc)
            output = tokenizer.decode(outputs[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"])
            print(output)


def load_configs(path: Path) -> list[SamplingConfig]:
    with path.open() as f:
        json_data = json.load(f)

    return pydantic.parse_obj_as(list[SamplingConfig], json_data)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, default="facebook/galactica-125m")
    parser.add_argument(
        "--mode",
        type=str,
        default="legacy",
        help="legacy, v2",
    )
    parser.add_argument("--prompt-file", type=str)
    parser.add_argument("--samples", type=int, default=3, help="Number of continuations to generaret")
    parser.add_argument("--seed", type=int, default="42", help="psoudo random number generator seed")
    parser.add_argument("-n", type=int)
    parser.add_argument("--config", type=str, default="config/default.json")
    return parser.parse_args()


def main():
    print("Using pytorch version {}".format(torch.__version__))

    args = parse_args()
    print("Args:", args)

    # load configuration
    sampling_configs = load_configs(Path(args.config))

    model_name = args.model_name
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.add_special_tokens({"pad_token": "<|endoftext|>"})
    model = AutoModelForCausalLM.from_pretrained(model_name).eval().cuda()

    print(f"Loading prompts: {args.prompt_file}")
    prompts = load_jsonl(args.prompt_file)
    print(f"prompts: {len(prompts)}")

    if args.n:
        prompts = prompts[: args.n]

    sample_prompt_continuations(
        prompts=prompts, model=model, tokenizer=tokenizer, mode=args.mode, sampling_configs=sampling_configs
    )


if __name__ == "__main__":
    main()
