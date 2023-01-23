QA_SPECIAL_TOKENS = {"Question": "<human>", "Answer": "<bot>", "StartPrefix": "<prefix>", "EndPrefix": "</prefix>"}


def format_pair(pair):
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pair[0], QA_SPECIAL_TOKENS["Answer"]), pair[1]
