import argparse
import gzip
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import pydantic
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer

QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


class SamplingConfig(pydantic.BaseModel):
    name: str
    generate_args: dict[str, Any]
    pre_text: str

    # for legacy models
    human_name: str = "User"
    bot_name: str = "Joi"


class Configuration(pydantic.BaseModel):
    default_args: dict[str, Any]
    configurations: list[SamplingConfig]


class SamplingResult(pydantic.BaseModel):
    sampling_config: str
    sampling_params: dict
    output: str


class PromptResults(pydantic.BaseModel):
    prompt: str
    results: list[SamplingResult]


class SamplingReport(pydantic.BaseModel):
    model_name: str
    date: str
    prompts: list[PromptResults]


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


def sample(
    prompt: str,
    model,
    tokenizer: PreTrainedTokenizer,
    mode: str,
    sampling_config: SamplingConfig,
    default_args: dict,
    device: torch.DeviceObjType,
):
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

    sampling_params = default_args.copy()
    for k, v in sampling_config.generate_args.items():
        sampling_params[k] = v

    inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(device)
    input_ids = inputs.input_ids
    outputs = model.generate(
        input_ids,
        **sampling_params,
        early_stopping=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    output_tokens = outputs[0, input_ids.size(1) :]
    return output_tokens, sampling_params


def sample_prompt_continuations(
    prompts: list[str],
    model,
    tokenizer: PreTrainedTokenizer,
    mode: str,
    config: Configuration,
    device: torch.DeviceObjType,
    verbose: bool = False,
) -> list[PromptResults]:
    prompt_results: list[PromptResults] = []
    for p in tqdm(prompts):
        sampling_results: list[SamplingResult] = []
        for sc in config.configurations:
            output_tokens, sampling_params = sample(
                p,
                model=model,
                tokenizer=tokenizer,
                mode=mode,
                sampling_config=sc,
                default_args=config.default_args,
                device=device,
            )
            output = tokenizer.decode(
                output_tokens, truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"], skip_special_tokens=True
            )

            if verbose:
                print(f"===[ Config: {sc.name} ]===\n")
                print(f'User: "{p}"')
                print(f'Assistant: "{output}"\n')

            sampling_results.append(
                SamplingResult(sampling_config=sc.name, sampling_params=sampling_params, output=output)
            )

        prompt_results.append(PromptResults(prompt=p, results=sampling_results))
    return prompt_results


def load_configs(path: Path) -> Configuration:
    with path.open() as f:
        json_data = json.load(f)

    return pydantic.parse_obj_as(Configuration, json_data)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda", type=str, help="device to use")
    parser.add_argument("--device-index", default=1, type=int, help="device index")
    parser.add_argument("--model-name", type=str, default="facebook/galactica-125m")
    parser.add_argument(
        "--mode",
        type=str,
        default="legacy",
        help="legacy, v2",
    )
    parser.add_argument("--prompt-file", type=str, help="jsonl string prompts input file name")
    parser.add_argument("--report", type=str, help="json sampling report output file name", default="report.json")
    parser.add_argument("--seed", type=int, default="42", help="psoudo random number generator seed")
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("-n", type=int)
    parser.add_argument("--config", type=str, default="config/default.json")
    return parser.parse_args()


def main():
    print("Using pytorch version {}".format(torch.__version__))

    args = parse_args()
    print("Args:", args)

    device = torch.device(args.device, args.device_index)
    print("Device:", device)

    if args.seed:
        random.seed(args.seed)
        torch.manual_seed(args.seed)

    # load configuration
    config = load_configs(Path(args.config))

    model_name = args.model_name
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.add_special_tokens({"pad_token": "<|endoftext|>"})
    model = AutoModelForCausalLM.from_pretrained(model_name).eval()
    model = model.to(device)

    print(f"Loading prompts: {args.prompt_file}")
    prompts = load_jsonl(input_file_path=args.prompt_file)
    print(f"prompt count: {len(prompts)}")

    if args.n:
        prompts = prompts[: args.n]

    report = SamplingReport(
        model_name=model_name,
        date=datetime.utcnow().isoformat(),
        prompts=sample_prompt_continuations(
            prompts=prompts,
            model=model,
            tokenizer=tokenizer,
            mode=args.mode,
            config=config,
            verbose=args.verbose,
            device=device,
        ),
    )

    report_path = Path(args.report)
    with report_path.open(mode="wt", encoding="UTF-8") as rf:
        x = report.dict(exclude_none=True)
        json.dump(x, rf, indent=2)


if __name__ == "__main__":
    main()
