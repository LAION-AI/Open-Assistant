import argparse
from distutils.util import strtobool as strtoboolint

import transformers
from tokenizer import build_tokenizer
from transformers.utils import cached_file


def strtobool(s: str) -> bool:
    return bool(strtoboolint(s))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tokenizer_type", type=str, default="SentencePieceTokenizer", help="SentencePieceTokenizer or FalconTokenizer"
    )
    parser.add_argument(
        "--vocab_file", type=str, help="[optional] vocab file for SentencePiece (get from HF cache by default)"
    )
    parser.add_argument(
        "--tokenizer_name",
        type=str,
        default="meta-llama/Llama-2-7b-hf",
        help="HuggingFace repo name or path, e.g. 'meta-llama/Llama-2-7b-hf' or 'tiiuae/falcon-40b'",
    )
    parser.add_argument("--cache_dir", type=str, default=None, help="Huggingface cache directory ")
    parser.add_argument(
        "--vocab_extra_ids_list",
        type=str,
        default="<|im_start|>,<|im_end|>",
        help='Comma separated list of additional tokens (e.g. "<|im_start|>,<|im_end|>")',
    )
    parser.add_argument("--output_dir", type=str, default="output", help="Path of output directory")
    return parser.parse_args()


def main():
    """
    Usage examples:
    python create_hf_tokenizer_config.py --tokenizer_type SentencePieceTokenizer --tokenizer_name meta-llama/Llama-2-7b-hf --output_dir output
    python create_hf_tokenizer_config.py --tokenizer_type FalconTokenizer --tokenizer_name tiiuae/falcon-40b --output_dir output
    """
    args = parse_args()
    print("Configuration:")
    for k, v in vars(args).items():
        print(f"{k}: {v}")

    hf_tokenizer = transformers.AutoTokenizer.from_pretrained(args.tokenizer_name, cache_dir=args.cache_dir)

    print("tokenizer.vocab_files_names", hf_tokenizer.vocab_files_names)

    if args.tokenizer_type == "FalconTokenizer":
        args.vocab_file = ""
    elif args.vocab_file is None:
        args.vocab_file = cached_file(
            args.tokenizer_name, hf_tokenizer.vocab_files_names["vocab_file"], cache_dir=args.cache_dir
        )

    # add default args for megatron tokenizer
    args.rank = 0
    args.vocab_extra_ids = 0
    args.new_tokens = True
    args.make_vocab_size_divisible_by = 128
    args.tensor_model_parallel_size = 1
    mt_tokenizer = build_tokenizer(args)

    if args.tokenizer_type == "SentencePieceTokenizer":
        print("_special_tokens", mt_tokenizer._special_tokens)
        print("additional_special_tokens_ids", mt_tokenizer.additional_special_tokens_ids)

        hf_tokenizer.add_tokens("<CLS>", special_tokens=True)
        hf_tokenizer.add_tokens("<SEP>", special_tokens=True)
        hf_tokenizer.add_tokens("<EOD>", special_tokens=True)
        hf_tokenizer.add_tokens("<MASK>", special_tokens=True)
        hf_tokenizer.add_tokens("<PAD>", special_tokens=True)
        hf_tokenizer.cls_token_id = mt_tokenizer.cls
        hf_tokenizer.sep_token_id = mt_tokenizer.sep
        hf_tokenizer.mask_token_id = mt_tokenizer.mask
        hf_tokenizer.pad_token_id = mt_tokenizer.pad

        additional_special_tokens = hf_tokenizer.additional_special_tokens
        special_tokens = {"additional_special_tokens": additional_special_tokens}
        if args.vocab_extra_ids_list:
            additional_special_tokens.extend(args.vocab_extra_ids_list.split(","))

        hf_tokenizer.add_special_tokens(special_tokens_dict=special_tokens, replace_additional_special_tokens=True)

        additional_special_tokens_ids = [mt_tokenizer.vocab.get(t) for t in additional_special_tokens]
        hf_tokenizer.additional_special_tokens_ids = additional_special_tokens_ids

        tokens_to_check = [
            v for k, v in hf_tokenizer.special_tokens_map.items() if k != "additional_special_tokens"
        ] + additional_special_tokens
        print("checking token ids:")
        for t in tokens_to_check:
            a = mt_tokenizer.vocab.get(t)
            b = hf_tokenizer.vocab.get(t)
            print(f"{t}: {a} (mt) == {b} (hf)")
            assert a == b, "Mismatch between megatron and huggingface tokenizer vocabularies"
    elif args.tokenizer_type == "FalconTokenizer":
        hf_tokenizer = mt_tokenizer.tokenizer
    else:
        raise RuntimeError(f"Unsupported tokenizer type: {args.tokenizer_type}")

    print("special_tokens_map:", hf_tokenizer.special_tokens_map)

    hf_tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
