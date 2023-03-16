QA_SPECIAL_TOKENS = {
    "Question": "<|prompter|>",
    "Answer": "<|assistant|>",
    "System": "<|system|>",
    "StartPrefix": "<|prefix_begin|>",
    "EndPrefix": "<|prefix_end|>",
}


def format_system_prefix(prefix, eos_token):
    return "{}{}{}".format(
        QA_SPECIAL_TOKENS["System"],
        prefix,
        eos_token,
    )


def format_pairs(pairs, eos_token, add_initial_reply_token=False):
    conversations = [
        "{}{}{}".format(QA_SPECIAL_TOKENS["Question" if i % 2 == 0 else "Answer"], pairs[i], eos_token)
        for i in range(len(pairs))
    ]
    if add_initial_reply_token:
        conversations.append(QA_SPECIAL_TOKENS["Answer"])
    return conversations


def format_rl_text(pairs):
    # convert question answer pairs to only the prefix prompt for RLHF
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[0], QA_SPECIAL_TOKENS["Answer"])


def format_reply(text, eos_token):
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Answer"], text, eos_token)
