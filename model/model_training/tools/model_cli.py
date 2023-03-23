#!/usr/bin/env python3
import argparse
import time

import torch
import transformers
from model_training.custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pairs, format_system_prefix
from model_training.models import get_specific_model
from model_training.utils import _strtobool
from tokenizers import pre_tokenizers

if __name__ == "__main__":
    import warnings

    warnings.filterwarnings("ignore")

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--max_new_tokens", type=int, default=200)
    parser.add_argument("--top_k", type=int, default=40)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--do-sample", type=_strtobool, default=True)
    parser.add_argument("--format", type=str, default="v2")
    parser.add_argument("--8bit", action="store_true", dest="eightbit")
    parser.add_argument("--system_prefix", type=str, default=None)
    parser.add_argument("--per-digit-tokens", action="store_true")
    args = parser.parse_args()

    if args.eightbit:
        model = get_specific_model(
            args.model_path,
            load_in_8bit=True,
            device_map="auto",
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16,
            offload_state_dict=True,
        )
    else:
        model = get_specific_model(args.model_path)

    model.gradient_checkpointing_enable()  # reduce number of stored activations
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model_path)
    if args.per_digit_tokens:
        tokenizer._tokenizer.pre_processor = pre_tokenizers.Digits(True)

    human_token_id = tokenizer.additional_special_tokens_ids[
        tokenizer.additional_special_tokens.index(QA_SPECIAL_TOKENS["Question"])
    ]

    print('Type "quit" to exit')
    print("Press Control + C to restart conversation (spam to exit)")

    conversation_history = []

    while True:
        try:
            user_input = input("User: ")
            if user_input == "quit":
                break

            conversation_history.append(user_input)

            batch = tokenizer.encode(
                format_system_prefix(args.system_prefix, tokenizer.eos_token)
                if args.system_prefix
                else ""
                + "".join(format_pairs(conversation_history, tokenizer.eos_token, add_initial_reply_token=True)),
                return_tensors="pt",
            )

            with torch.cuda.amp.autocast():
                out = model.generate(
                    input_ids=batch.to(model.device),
                    max_new_tokens=args.max_new_tokens,
                    do_sample=args.do_sample,
                    top_k=args.top_k,
                    temperature=args.temperature,
                    eos_token_id=human_token_id,
                    pad_token_id=tokenizer.eos_token_id,
                )

            if out[0][-1] == tokenizer.eos_token_id:
                response = out[0][:-1]
            else:
                response = out[0]

            response = tokenizer.decode(out[0]).split(QA_SPECIAL_TOKENS["Answer"])[-1]
            print(f"Bot: {response}")
            conversation_history.append(response)
        except KeyboardInterrupt:
            conversation_history = []
            print()
            print("Conversation restarted")
            time.sleep(1)
            continue
        except EOFError:  # Catch ctrl+d
            print()
            break
