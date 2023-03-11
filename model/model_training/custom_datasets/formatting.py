from enum import Enum

QA_SPECIAL_TOKENS = {
    "Question": "<|prompter|>",
    "Answer": "<|assistant|>",
    "System": "<|system|>",
    "Start": "<|startoftext|>",
    "StartPrefix": "<|prefix_begin|>",
    "EndPrefix": "<|prefix_end|>",
}


class SeqToken(str, Enum):
    begin = "<|startoftext|>"
    end = "<|endoftext|>"
    delimiter = "\n"


class ChatRole(str, Enum):
    system = "<|system|>"
    prompter = "<|prompter|>"
    assistant = "<|assistant|>"


def format_pair(pairs):
    conversations = []
    for i, text in enumerate(pairs):
        if i % 2 == 0:
            text = f"{SeqToken.begin}{ChatRole.prompter}{SeqToken.delimiter}{text}{SeqToken.end}{SeqToken.begin}{ChatRole.assistant}{SeqToken.delimiter}"
        else:  # label mask = 1
            text = f"{text}{SeqToken.end}"
        conversations.append(text)

    return conversations


def format_rl_text(pairs):
    # convert question answer pairs to only the prefix prompt for RLHF
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[0], QA_SPECIAL_TOKENS["Answer"])
