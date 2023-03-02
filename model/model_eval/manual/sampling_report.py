import argparse
import gzip
import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pydantic
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer

QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


class SamplingConfig(pydantic.BaseModel):
    name: Optional[str]
    generate_args: dict[str, Any] = {}
    pre_text: Optional[str]

    # for legacy mode
    human_name: Optional[str]
    bot_name: Optional[str]


class Configuration(pydantic.BaseModel):
    default: Optional[SamplingConfig]
    configurations: list[SamplingConfig]


class SamplingResult(pydantic.BaseModel):
    sampling_config: str
    sampling_params: dict
    outputs: list[str]


class PromptResults(pydantic.BaseModel):
    prompt: str
    results: list[SamplingResult]


class SamplingReport(pydantic.BaseModel):
    model_name: str
    date: str
    args: dict
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
    device: torch.DeviceObjType,
):
    assert sampling_config.name, "'name' must be specified for sampling configuration"
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
        assert sc.human_name and sc.bot_name, "'human_name' and 'bot_name' parameters must be specified in config "
        input_text = f"{prefix}\n{sc.human_name}: {prompt}\n\n{sc.bot_name}: "

    sampling_params = sampling_config.generate_args
    inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(device)
    input_ids = inputs.input_ids
    outputs = model.generate(
        input_ids,
        **sampling_params,
        pad_token_id=tokenizer.eos_token_id,
    )
    output_tokens = outputs[0, input_ids.size(1) :]
    return output_tokens, sampling_params


def merge_configs(*configs: tuple[Optional[SamplingConfig]]) -> Optional[SamplingConfig]:
    merged: SamplingConfig | None = None
    for c in configs:
        if not merged:
            if c:
                merged = c.copy(deep=True)
        else:
            # simple fields
            fields = ["name", "pre_text", "human_name", "bot_name"]
            for field_name in fields:
                v = getattr(c, field_name)
                if v:
                    setattr(merged, field_name, v)
            # generate args
            if c.generate_args:
                for k, v in c.generate_args.items():
                    merged.generate_args[k] = v

    return merged


def sample_prompt_continuations(
    prompts: list[str],
    model,
    tokenizer: PreTrainedTokenizer,
    mode: str,
    config: Configuration,
    device: torch.DeviceObjType,
    num_samples: int = 1,
    verbose: bool = False,
) -> list[PromptResults]:
    prompt_results: list[PromptResults] = []
    for p in tqdm(prompts):
        sampling_results: list[SamplingResult] = []
        for sc in config.configurations:
            outputs = []
            for i in range(num_samples):
                if i > 0 and sc.generate_args.get("do_sample") is False:
                    break  # don't repeat greedy sampling
                output_tokens, sampling_params = sample(
                    p,
                    model=model,
                    tokenizer=tokenizer,
                    mode=mode,
                    sampling_config=merge_configs(config.default, sc),
                    device=device,
                )
                output = tokenizer.decode(
                    output_tokens, truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"], skip_special_tokens=True
                )

                if verbose:
                    print(f"===[ Config: {sc.name} [{i+1}/{num_samples}] ]===\n")
                    print(f'User: "{p}"')
                    print(f'Assistant: "{output}"\n')
                outputs.append(output)

            sampling_results.append(
                SamplingResult(sampling_config=sc.name, sampling_params=sampling_params, outputs=outputs)
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
    parser.add_argument("--device-index", default=0, type=int, help="device index")
    parser.add_argument("--model-name", type=str, default="facebook/galactica-125m")
    parser.add_argument(
        "--mode",
        type=str,
        default="legacy",
        help="legacy, v2",
    )
    parser.add_argument(
        "--prompts", type=str, help="jsonl string prompts input file name", default="./data/en_100_text.jsonl.gz"
    )
    parser.add_argument("--report", type=str, help="json sampling report output file name")
    parser.add_argument("--seed", type=int, default="42", help="psoudo random number generator seed")
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("-n", type=int)
    parser.add_argument("--num-samples", type=int, default=2)
    parser.add_argument("--config", type=str, default="config/default.json")
    parser.add_argument("--half", action="store_true", default=False, help="use float16")
    return parser.parse_args()


def main():
    """
    Usage example:
    python sampling_report.py --model-name facebook/galactica-125m --config config/default.json --prompts data/en_100_text.jsonl --report report_file.json -n 10 --verbose

    eval oasst model:
    python sampling_report.py --model-name theblackcat102/pythia-3b-deduped-sft --mode v2 --config config/default.json --prompts data/en_100_text.jsonl -n 2 --verbose
    """

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
    tokenizer.eos_token_id = model.config.eos_token_id
    if args.half:
        model = model.half()
    model = model.to(device)

    print(f"Loading prompts file: {args.prompts}")
    prompts = load_jsonl(input_file_path=args.prompts)
    print(f"prompt count: {len(prompts)}")

    if args.n:
        prompts = prompts[: args.n]

    report = SamplingReport(
        model_name=model_name,
        date=datetime.utcnow().isoformat(),
        args=vars(args),
        prompts=sample_prompt_continuations(
            prompts=prompts,
            model=model,
            tokenizer=tokenizer,
            mode=args.mode,
            config=config,
            num_samples=args.num_samples,
            verbose=args.verbose,
            device=device,
        ),
    )

    preport_filename = args.report
    if not preport_filename:
        save_model_name = re.sub(r"[^\w\d-]", "_", model_name)
        preport_filename = f"{save_model_name}_sampling.json"
    print("preport_filename", preport_filename)

    report_path = Path(preport_filename)
    print(f"writing report: {str(report_path)}")
    with report_path.open(mode="wt", encoding="UTF-8") as rf:
        x = report.dict(exclude_none=True)
        json.dump(x, rf, indent=2)


if __name__ == "__main__":
    main()
