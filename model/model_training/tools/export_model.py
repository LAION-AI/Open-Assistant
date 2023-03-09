import argparse
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", type=str, help="checkpoint path or model name")
    parser.add_argument("--dtype", type=str, default="float16", help="float16 or float32")
    parser.add_argument("--hf_repo_name", type=str, help="Huggingface repository name")
    parser.add_argument("--auth_token", type=str, help="User access token")
    parser.add_argument("--output_folder", type=str, help="output folder path")
    parser.add_argument("--max_shard_size", type=str, default="10GB")
    parser.add_argument("--cache_dir", type=str)
    return parser.parse_args()


def main():
    args = parse_args()

    if args.dtype in ("float16", "fp16"):
        torch_dtype = torch.float16
    elif args.dtype in ("float32", "fp32"):
        torch_dtype = torch.float32
    else:
        print(f"Unsupported dtpye: {args.dtype}")
        sys.exit(1)

    if not args.hf_repo_name and not args.output_folder:
        print(
            "Please specify either `--hf_repo_name` to push to HF or `--output_folder` "
            "to export the model to a local folder."
        )
        sys.exit(1)

    print(f"Loading tokenizer '{args.model_name}' ...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    print(f"{type(tokenizer).__name__} (vocab_size={len(tokenizer)})")

    print(f"Loading model '{args.model_name}' ({args.dtype}) ...")
    model = AutoModelForCausalLM.from_pretrained(args.model_name, torch_dtype=torch_dtype, cache_dir=args.cache_dir)
    print(f"{type(model).__name__} (num_parameters={model.num_parameters()})")

    if args.output_folder:
        print(f"Saving model to: {args.output_folder}")
        model.save_pretrained(args.output_folder, max_shard_size=args.max_shard_size)

        print(f"Saving tokenizer to: {args.output_folder}")
        tokenizer.save_pretrained(args.output_folder)

    if args.hf_repo_name:
        print("Uploading model to HF...")
        model.push_to_hub(args.hf_repo_name, use_auth_token=args.auth_token, max_shard_size=args.max_shard_size)

        print("Uploading tokenizer to HF...")
        tokenizer.push_to_hub(args.hf_repo_name, use_auth_token=args.auth_token)


if __name__ == "__main__":
    main()
