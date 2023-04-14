from dataclasses import dataclass
from enum import Enum
from itertools import zip_longest

QA_SPECIAL_TOKENS = {
    "Question": "<|prompter|>",
    "Answer": "<|assistant|>",
    "System": "<|system|>",
    "StartPrefix": "<|prefix_begin|>",
    "EndPrefix": "<|prefix_end|>",
}


class Mode(Enum):
    sft = "sft"
    rm = "rm"
    rl = "rl"


def format_system_prefix(prefix, eos_token):
    return "{}{}{}".format(
        QA_SPECIAL_TOKENS["System"],
        prefix,
        eos_token,
    )


@dataclass
class DatasetEntry:
    questions: list[str]
    answers: list[str]
    context: str | None

    def get_formatted(self, mode: Mode, eos_token: str):
        # todo: test
        if self.context is not None:
            first_entry = f"{QA_SPECIAL_TOKENS['System']}{self.context}{eos_token}"
            qa_list = [first_entry]
        else:
            qa_list = list()
        if mode == Mode.rl:
            if self.context is not None:
                return f"{QA_SPECIAL_TOKENS['System']}{self.context}{eos_token}{QA_SPECIAL_TOKENS['Question']}{self.questions[0]}{QA_SPECIAL_TOKENS['Answer']}"
            else:
                return f"{QA_SPECIAL_TOKENS['Question']}{self.questions[0]}{QA_SPECIAL_TOKENS['Answer']}"
        for q, a in zip_longest(self.questions, self.answers):
            match (q, a):
                case (str(), str()):
                    qa_list.extend(
                        [
                            f"{QA_SPECIAL_TOKENS['Question']}{q}{eos_token}",
                            f"{QA_SPECIAL_TOKENS['Answer']}{a}{eos_token}",
                        ]
                    )
                case (str(), None):
                    qa_list.append(f"{QA_SPECIAL_TOKENS['Question']}{q}{eos_token}")
                case (None, None):
                    break
                case (None, str()):
                    import pdb

                    pdb.set_trace()
                    raise ValueError("Received answer without getting corresponding question. Aborting")
        if mode == Mode.sft:
            return qa_list
        elif mode == Mode.rm:
            raise NotImplementedError("This is currently not implemented.")

    @classmethod
    def create_from_prompter_assistant_interplay(cls, qa: dict[str, str]):
        """Creates a DatasetEntry from a qa of given structure. Even if qa contains consecutative assistant or prompter phrases.


        Returns:
            self: DatasetEntry class
        """
        # todo: implement
        pass


def format_pairs(
    pairs: list[str] | DatasetEntry, eos_token: str, add_initial_reply_token: str = False, mode: Mode | None = None
) -> list[str]:
    if isinstance(pairs, DatasetEntry) and mode is not None:
        return pairs.get_formatted(mode=mode, eos_token=eos_token)
    else:
        # backwards compatibility
        conversations = [
            "{}{}{}".format(QA_SPECIAL_TOKENS["Question" if i % 2 == 0 else "Answer"], pairs[i], eos_token)
            for i in range(len(pairs))
        ]
        if add_initial_reply_token:
            conversations.append(QA_SPECIAL_TOKENS["Answer"])
        return conversations


def format_rl_text(pairs: list[str]) -> str:
    # convert question answer pairs to only the prefix prompt for RLHF
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Question"], pairs[0], QA_SPECIAL_TOKENS["Answer"])


def format_reply(text: str, eos_token: str) -> str:
    return "{}{}{}".format(QA_SPECIAL_TOKENS["Answer"], text, eos_token)
