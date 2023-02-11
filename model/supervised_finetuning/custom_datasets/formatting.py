QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


def format_pair(pairs):
    assert len(pairs) % 2 == 0
    return [
        "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[i], QA_SPECIAL_TOKENS["Answer"])
        if i % 2 == 0
        else pairs[i]
        for i in range(0, len(pairs), 2)
    ]
