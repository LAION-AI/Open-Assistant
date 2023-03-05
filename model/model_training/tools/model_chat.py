"""

A very simple script to test model locally


"""
import argparse

from custom_datasets.formatting import QA_SPECIAL_TOKENS
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils import _strtobool

parser = argparse.ArgumentParser()
parser.add_argument("--model_path", type=str, required=True)
parser.add_argument("--bot_name", type=str, default="Joi", help="Use this when your format isn't in OA format")
parser.add_argument("--format", type=str, default="v2")
parser.add_argument("--max_new_tokens", type=int, default=200)
parser.add_argument("--top_k", type=int, default=40)
parser.add_argument("--temperature", type=float, default=1.0)
parser.add_argument("--do-sample", type=_strtobool, default=True)
args = parser.parse_args()

bot_name = args.bot_name
model_name = args.model_path
method = args.format


def talk(human_input, history, sep_token, prefix=""):
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


def process_output(output):
    if method == "v2":
        answer = output.split(QA_SPECIAL_TOKENS["Answer"])[-1]
        answer = answer.split("</s>")[0].replace("<|endoftext|>", "").lstrip().split(QA_SPECIAL_TOKENS["Answer"])[0]
    else:
        answer = output.split("\n\n{}:".format(bot_name))[-1]
        answer = answer.split("</s>")[0].replace("<|endoftext|>", "").lstrip().split("\n\n{}:".format(bot_name))[0]
    return answer


tokenizer = AutoTokenizer.from_pretrained(model_name)
if method != "v2":
    tokenizer.add_special_tokens({"pad_token": "<|endoftext|>"})
model = AutoModelForCausalLM.from_pretrained(model_name).half().eval().cuda()

if __name__ == "__main__":
    histories = []
    prefix = ""
    while True:
        print(">", end=" ")
        prompt = input()
        if prompt == "!reset":
            histories = []
        else:
            input_text = talk(prompt, histories, prefix)
            inputs = tokenizer(input_text, return_tensors="pt", padding=True).to(0)
            outputs = model.generate(
                **inputs,
                early_stopping=True,
                max_new_tokens=args.max_new_tokens,
                do_sample=True,
                top_k=args.top_k,
                temperature=args.temperature,
                pad_token_id=tokenizer.eos_token_id,
                # dialogue_collator.py line 36
            )
            output = tokenizer.decode(outputs[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"])
            reply = process_output(output)

            if len(reply) != 0:
                print(reply)
                histories.append((prompt, reply))
            else:
                print("emtpy token")
