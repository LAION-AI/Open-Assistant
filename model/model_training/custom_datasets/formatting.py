QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


def format_pair(pairs):
    return [
        "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[i], QA_SPECIAL_TOKENS["Answer"])
        if i % 2 == 0
        else pairs[i]
        for i in range(len(pairs))
    ]
