from itertools import zip_longest
from random import random, shuffle

from langcodes import Language
from model_training.custom_datasets.entities import Mode
from pydantic import BaseModel, validator
from pydantic.fields import ModelField

SYSTEM_PROPERTY_DROP_PROBA = 0.5

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


class PretrainDatasetEntry(BaseModel):
    text: str | None = None


class DatasetEntry(BaseModel):
    questions: list[str]
    answers: list[str] | list[list[str]]
    context: str | None = None
    lang: str | None = None
    length: int | None = None
    quality: float | None = None
    humor: float | None = None
    creativity: float | None = None

    @validator("lang")
    def valid_lang(cls, v) -> str | None:
        if v is not None:
            if not (lang := Language.get(v)).is_valid():
                raise ValueError(f"Language {v} is not valid. Please provide BCP 47 compatible language codes.")
            return str(lang)

    @validator("length")
    def above_zero(cls, v) -> int:
        if v is not None and v < 0:
            raise ValueError(f"Length cannot be lower than 0. Received {v}")
        return v

    @validator("quality", "humor", "creativity")
    def between_0_1(cls, v, field: ModelField) -> float:
        if v is not None and not (0 <= v <= 1):
            raise ValueError(f"Field {field.name} must be between 0 and 1. Received {v}.")
        return round(v, 1)

    def system_tag(self, eos_token: str) -> str | None:
        relevant_system_infos = [
            (k, v)
            for k, v in self.__dict__.items()
            if k not in ["questions", "answers"]
            and v is not None
            and str(v).replace("\n", "")
            and random() > SYSTEM_PROPERTY_DROP_PROBA
        ]
        if len(relevant_system_infos) > 0:
            shuffle(relevant_system_infos)
            system_tag_key_values = "\n".join([f"{k}: {v}" for k, v in relevant_system_infos])
            system_tag = f"{QA_SPECIAL_TOKENS['System']}{system_tag_key_values}\n{eos_token}"
            return system_tag

    def _get_formatted_rm(self, eos_token: str, max_replies: int, system_tag: None | str):
        if isinstance(self.answers[0], list):
            answers = self.answers[0]
        else:
            answers = self.answers
        assert len(answers) > 1 and max_replies > 1
        answers = answers[:max_replies]
        match len(self.questions):
            case 0:
                question = ""
                # todo: not sure if this case is correct but it is equivalent to current non-dataset entry behaviour
                answers = [f"{a}{eos_token}" for a in answers]
            case 1:
                question = f"{QA_SPECIAL_TOKENS['Question']}{self.questions[0]}{eos_token}"
                answers = [f"{QA_SPECIAL_TOKENS['Answer']}{a}{eos_token}" for a in answers]
            case _:
                raise ValueError("Received more than one question in RM mode. This is unexpected. Aborting")
        if system_tag is not None:
            question = f"{system_tag}{question}"
        return (question, answers)

    def get_formatted(self, mode: Mode, eos_token: str, **kwargs) -> str | list[str] | tuple[str, list[str]]:
        system_tag = self.system_tag(eos_token)
        if mode == Mode.rl:
            if system_tag is not None:
                return f"{system_tag}{QA_SPECIAL_TOKENS['Question']}{self.questions[0]}{QA_SPECIAL_TOKENS['Answer']}"
            else:
                return f"{QA_SPECIAL_TOKENS['Question']}{self.questions[0]}{QA_SPECIAL_TOKENS['Answer']}"
        elif mode == Mode.rm:
            return self._get_formatted_rm(
                eos_token=eos_token, max_replies=kwargs.get("max_replies", 5), system_tag=system_tag
            )
        else:
            if system_tag is not None:
                qa_list = [system_tag]
            else:
                qa_list = list()
            # check if this is a RM capable dataset (so it has multiple answers to the same question)
            # and if so, extract just the highest scoring answer
            if isinstance(self.answers[0], list):
                answers = [answer[0] for answer in self.answers]
            else:
                answers = self.answers
            for q, a in zip_longest(self.questions, answers):
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
                        raise ValueError("Received answer without getting corresponding question. Aborting")
            return qa_list

    @classmethod
    def create_from_prompter_assistant_interplay(cls, qa: dict[str, str]):
        """Creates a DatasetEntry from a qa of given structure. Even if qa contains consecutative assistant or prompter phrases.


        Returns:
            self: DatasetEntry class
        """
        # todo: implement
        NotImplementedError("Function not implemented currently.")


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
