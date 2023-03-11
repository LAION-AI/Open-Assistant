#!/usr/bin/env python3
import argparse
import os
import sys
import time

import torch
import transformers

if __name__ == "__main__":
    import warnings

    warnings.filterwarnings("ignore")

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from custom_datasets.formatting import QA_SPECIAL_TOKENS, format_pair
    from models import get_specific_model
    from utils import _strtobool

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--max_new_tokens", type=int, default=200)
    parser.add_argument("--top_k", type=int, default=40)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--do-sample", type=_strtobool, default=True)
    parser.add_argument("--8bit", action="store_true", dest="eightbit")
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

            pairs = format_pair(conversation_history)
            pairs = ["{}{}".format(p, tokenizer.eos_token) for p in pairs]
            pairs.append(QA_SPECIAL_TOKENS["Answer"])
            batch = tokenizer.encode("".join(pairs), return_tensors="pt")

            with torch.cuda.amp.autocast():
                out = model.generate(
                    input_ids=batch.to(model.device),
                    max_new_tokens=args.max_new_tokens,
                    do_sample=True,
                    top_k=args.top_k,
                    temperature=args.temperature,
                    eos_token_id=human_token_id,
                    pad_token_id=tokenizer.eos_token_id,
                )

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
