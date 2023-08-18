import argparse
import sys

import model_training.models.reward_model  # noqa: F401 make sure reward model is registered for AutoModel
import torch
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", type=str, help="checkpoint path or model name")
    parser.add_argument("--dtype", type=str, default="fp16", help="fp16, bf16 or fp32")
    parser.add_argument("--hf_repo_name", type=str, help="Huggingface repository name")
    parser.add_argument("--auth_token", type=str, help="User access token")
    parser.add_argument("--output_folder", type=str, help="output folder path")
    parser.add_argument("--max_shard_size", type=str, default="10GB")
    parser.add_argument("--cache_dir", type=str)
    parser.add_argument("--reward_model", action="store_true", default=False)
    parser.add_argument("--rl_checkpoint", type=str, help="load RL fine-tuning checkpoint")
    parser.add_argument(
        "--rope_scaling_type", type=str, help="set rope scaling type (linear, dynamic)", default="linear"
    )
    parser.add_argument("--rope_scaling_factor", type=float, help="set rope scaling factor (float >1.0)")
    parser.add_argument(
        "--trust_remote_code",
        action="store_true",
        default=False,
        help="allow custom model code (required for Falcon)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(args)

    if args.dtype in ("float16", "fp16"):
        torch_dtype = torch.float16
    elif args.dtype in ("float32", "fp32"):
        torch_dtype = torch.float32
    elif args.dtype in ("bfloat16", "bf16"):
        torch_dtype = torch.bfloat16
    else:
        print(f"Unsupported dtype: {args.dtype}")
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

    if args.rl_checkpoint:
        model = AutoModelForCausalLM.from_pretrained(args.model_name, torch_dtype=torch_dtype, cache_dir=args.cache_dir)

        print(f"Loading RL checkpoint: {args.rl_checkpoint}...")
        checkpoint_state = torch.load(args.rl_checkpoint, map_location="cpu")["module"]

        # drop parameters of value head
        for param_name in ("v_head.0.weight", "v_head.0.bias", "v_head.2.weight", "v_head.2.bias"):
            checkpoint_state.pop(param_name, None)

        # resolve inconsistencies in the vocab size
        target_size = checkpoint_state[list(filter(lambda x: "embed" in x, list(checkpoint_state.keys())))[0]].shape[0]
        model.resize_token_embeddings(target_size)

        print(model.load_state_dict(checkpoint_state))

    elif args.reward_model:
        model = AutoModelForSequenceClassification.from_pretrained(
            args.model_name, torch_dtype=torch_dtype, cache_dir=args.cache_dir
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.model_name,
            torch_dtype=torch_dtype,
            cache_dir=args.cache_dir,
            trust_remote_code=args.trust_remote_code,
        )
    print(f"{type(model).__name__} (num_parameters={model.num_parameters()})")

    print("Model architecture:")
    print(model)

    if args.rope_scaling_type is not None and args.rope_scaling_factor is not None:
        assert args.rope_scaling_type in ("linear", "dynamic")
        assert args.rope_scaling_factor >= 1.0
        rope_scaling = {"type": args.rope_scaling_type, "factor": args.rope_scaling_factor}
        print(f"setting new rope_scaling config: {rope_scaling} (old: {model.config.rope_scaling})")
        model.config.rope_scaling = rope_scaling

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
