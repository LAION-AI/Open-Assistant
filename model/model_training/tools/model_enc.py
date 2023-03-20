import argparse
import os

import torch
from convert_llama_weights_to_hf import write_model, write_tokenizer
from transformers import AutoModelForCausalLM


def xor_files(file1, file2, output_file):
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        f1_data = f1.read()
        f2_data = f2.read()
        if len(f1_data) > len(f2_data):
            xor_data = bytes([a ^ b for a, b in zip(f1_data[: len(f2_data)], f2_data)])
            xor_data += bytes([a ^ f2_data[-1] for a in f1_data[len(f2_data) :]])
        elif len(f1_data) < len(f2_data):
            xor_data = bytes([a ^ b for a, b in zip(f1_data, f2_data[: len(f1_data)])])
            xor_data += bytes([f1_data[-1] ^ b for b in f2_data[len(f1_data) :]])
        else:
            xor_data = bytes([a ^ b for a, b in zip(f1_data, f2_data)])
        with open(output_file, "wb") as f:
            f.write(xor_data)


def xor_directories(dir1, dir2, output_dir, action):
    files1 = os.listdir(dir1)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for file in files1:
        if action == "encrypt":
            output_file = os.path.join(output_dir, file + ".enc")
        elif action == "decrypt":
            output_file = os.path.join(output_dir, file.replace(".enc", ""))
        else:
            raise ValueError("action must be either encrypt or decrypt")
        print(action, " file: ", output_file)
        if action == "encrypt":
            xor_files(os.path.join(dir1, file), os.path.join(dir2, file), output_file)
        elif action == "decrypt":
            xor_files(os.path.join(dir1, file), os.path.join(dir2, file + ".enc"), output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        help="action to perform",
    )
    parser.add_argument(
        "--input_dir",
        help="Location of LLaMA weights, which contains tokenizer.model and model folders",
    )
    parser.add_argument(
        "--model_size",
        choices=["7B", "13B", "30B", "65B", "tokenizer_only"],
    )
    parser.add_argument(
        "--output_dir",
        help="Location to write HF model and tokenizer",
    )
    parser.add_argument(
        "--encrypted_dir",
        help="Location of Encrypted LLaMA weights, which contains tokenizer.model and model folders",
    )
    parser.add_argument(
        "--to_encrypt_dir",
        help="Location of Encrypted LLaMA weights, which contains tokenizer.model and model folders",
    )
    args = parser.parse_args()

    # python script_to_convert.py convert_llama_to_hf --input_dir original_llama_weights/ --model_size 7B --output_dir converted_llama_weights/
    if args.action == "convert_llama_to_hf":
        # Convert Model
        write_model(
            model_path=os.path.join(args.output_dir, "llama-{}".format(args.model_size).lower()),
            input_base_path=os.path.join(args.input_dir, args.model_size),
            model_size=args.model_size,
        )
        write_tokenizer(
            tokenizer_path=os.path.join(args.output_dir, "tokenizer"),
            input_tokenizer_path=os.path.join(args.input_dir, "tokenizer.model"),
        )

        # re-save to match same file structure as finetunned weights
        model_path = os.path.join("./", args.output_dir, "llama-{}".format(args.model_size).lower())
        weights_hf_path = os.path.join("./", args.output_dir, "weights-hf")
        model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16)
        model.save_pretrained(save_directory=weights_hf_path, max_shard_size="10GB")

    elif args.action == "encrypt":
        # python script_to_convert.py encrypt --input_dir converted_llama_weights/weights-hf/ --output_dir encrypted_weights/ --to_encrypt_dir finetuned_weights/
        # Encrypt Model
        # e.g usage xor_directories('./converted_llama_weights', './finetuned_weights', './encrypted_weights')
        # xor_directories(args.input_dir, args.output_dir, args.to_encrypt_dir, "encrypt")
        xor_directories(args.input_dir, args.to_encrypt_dir, args.output_dir, "encrypt")

    elif args.action == "decrypt":
        # python script_to_convert.py decrypt --input_dir converted_llama_weights/weights-hf/ --output_dir decrypted_weights/ --encrypted_dir encrypted_weights/
        # Decrypt Model
        # e.g usage xor_directories('./converted_llama_weights', './encrypted_weights', './decrypted_weights')
        # xor_directories(args.input_dir, args.encrypted_dir, args.output_dir, "decrypt")
        xor_directories(args.input_dir, args.encrypted_dir, args.output_dir, "decrypt")


if __name__ == "__main__":
    main()
