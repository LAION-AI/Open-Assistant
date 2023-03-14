#!/usr/bin/env python3
"""

A very simple script to test model locally


"""
import argparse
from typing import List, Tuple

if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_datasets.formatting import QA_SPECIAL_TOKENS
from tokenizers import pre_tokenizers
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils import _strtobool, process_output

parser = argparse.ArgumentParser()
parser.add_argument("--model_path", type=str, required=True)
parser.add_argument("--bot_name", type=str, default="Joi", help="Use this when your format isn't in OA format")
parser.add_argument("--format", type=str, default="v2")
parser.add_argument("--max_new_tokens", type=int, default=200)
parser.add_argument("--top_k", type=int, default=40)
parser.add_argument("--temperature", type=float, default=1.0)
parser.add_argument("--do-sample", type=_strtobool, default=True)
parser.add_argument("--per-digit-tokens", action="store_true")
args = parser.parse_args()

bot_name: str = args.bot_name
model_name: str = args.model_path
method: str = args.format


def talk(human_input: str, history: List[Tuple[str, str]], sep_token: str, prefix=""):
    histories = []
    if method == "v2":
        prefix = "<prefix>You are a helpful assistant called Joi trained by OpenAssistant on large corpus of data, you will now help user to answer the question as concise as possible</prefix>"
        for question, answer in history:
            histories.append(
                "{}{}{}{}".format(QA_SPECIAL_TOKENS["Question"], question, QA_SPECIAL_TOKENS["Answer"], answer)
            )
        if len(histories) > 0:
            prefix += sep_token.join(histories)
            # add sep at the end
            prefix += sep_token
        prefix += "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], human_input, QA_SPECIAL_TOKENS["Answer"])
    else:
        for question, answer in history:
            histories.append("User: " + question + "\n\n{}: ".format(bot_name) + answer + "\n")
        if len(histories) > 0:
            prefix += "\n".join(histories)
        prefix += "\nUser: " + human_input + "\n\n{}: ".format(bot_name)

    return prefix


tokenizer = AutoTokenizer.from_pretrained(model_name)
if method != "v2":
    tokenizer.add_special_tokens({"pad_token": "<|endoftext|>"})
if args.per_digit_tokens:
    tokenizer._tokenizer.pre_processor = pre_tokenizers.Digits(True)

model = AutoModelForCausalLM.from_pretrained(model_name).half().eval().cuda()

if __name__ == "__main__":
    histories = []
    prefix = ""
    while True:
        print(">", end=" ")
        try:
            prompt = input()
        except (EOFError, KeyboardInterrupt):  # Catch ctrl+d and ctrl+c respectively
            print()
            break
        if prompt == "!reset":
            histories = []
        else:
            input_text = talk(prompt, histories, prefix)
            inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(0)
            del inputs["token_type_ids"]
            outputs = model.generate(
                **inputs,
                early_stopping=True,
                max_new_tokens=args.max_new_tokens,
                do_sample=args.do_sample,
                top_k=args.top_k,
                temperature=args.temperature,
                pad_token_id=tokenizer.eos_token_id,
                # dialogue_collator.py line 36
            )
            output = tokenizer.decode(outputs[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"])
            reply = process_output(output, method, bot_name)

            if len(reply) != 0:
                print(reply)
                histories.append((prompt, reply))
            else:
                print("empty token")
