QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


def format_pair(pairs):
    return [
        "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[i], QA_SPECIAL_TOKENS["Answer"])
        if i % 2 == 0
        else pairs[i]
        for i in range(len(pairs))
    ]


def format_rl_text(pairs):
    # convert question answer pairs to only the prefix prompt for RLHF
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[0], QA_SPECIAL_TOKENS["Answer"])
