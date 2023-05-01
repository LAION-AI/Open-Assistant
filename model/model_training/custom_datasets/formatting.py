import re
from itertools import zip_longest
from random import random, shuffle
from typing import Optional

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


class Utterance(BaseModel):
    content: str

    length: int | None = None
    lang: str | None = None
    quality: int | None = None
    humor: int | None = None
    creativity: int | None = None
    context: str | None = None

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
    def between_0_10(cls, v, field: ModelField) -> float:
        if v is not None and not (0 <= v <= 10):
            raise ValueError(f"Field {field.name} must be between 0 and 10. Received {v}.")
        return round(v, 1)

    def system_tag(self, eos_token: str, property_dropout: float = 0.0) -> str | None:
        relevant_system_infos = [
            (k, v)
            for k, v in self.__dict__.items()
            if k not in ["content"] and v is not None and str(v).replace("\n", " ") and random() >= property_dropout
        ]

        if len(relevant_system_infos) == 0:
            return None

        shuffle(relevant_system_infos)
        system_tag_key_values = "\n".join([f"{k}: {v}" for k, v in relevant_system_infos])
        system_tag = f"{QA_SPECIAL_TOKENS['System']}{system_tag_key_values}\n{eos_token}"
        return system_tag


class DatasetEntry(BaseModel):
    # For a dialouge with [Q1, A1, Q2, A2]
    # questions: [Q1, Q2]
    # answers: [A1, A2]
    # the list[list[Utterance]] case is used for reward model datasets (which have multiple answers per prompt)
    questions: list[Utterance]
    answers: list[Utterance] | list[list[Utterance]]
    property_dropout: float = SYSTEM_PROPERTY_DROP_PROBA

    def _get_formatted_rm(self, eos_token: str, max_replies: int = 5):
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
                # todo: how to handle different system tags for the answers since the tag should be part of the question
                # answer_system_tags = [a.system_tag(eos_token=eos_token, property_dropout=self.property_dropout) or "" for a in answers]
                system_tag = self.questions[0].system_tag(eos_token=eos_token, property_dropout=self.property_dropout)
                question = f"{QA_SPECIAL_TOKENS['Question']}{self.questions[0].context}{eos_token}{system_tag}"
                answers = [f"{QA_SPECIAL_TOKENS['Answer']}{a}{eos_token}" for a in answers]
            case _:
                # todo: implement, especially oasst actually needs this
                raise ValueError("Received more than one question in RM mode. This is unexpected. Aborting")
        return (question, answers)

    def get_formatted(self, mode: Mode, eos_token: str, **kwargs) -> str | list[str] | tuple[str, list[str]]:
        if mode == Mode.rl:
            q = self.questions[0]
            system_tag = q.system_tag(eos_token=eos_token, property_dropout=self.property_dropout) or ""
            return f"{QA_SPECIAL_TOKENS['Question']}{q.content}{QA_SPECIAL_TOKENS['Answer']}{system_tag}"
        elif mode == Mode.rm:
            return self._get_formatted_rm(eos_token=eos_token, max_replies=kwargs.get("max_replies", 5))
        else:
            qa_list: list[str] = []

            # check if this is a RM capable dataset (so it has multiple answers to the same question)
            # and if so, extract just the highest scoring answer
            answers: list[Utterance]
            if isinstance(self.answers[0], list):
                answers = [answer[0] for answer in self.answers]
            else:
                answers = self.answers

            for q, a in zip_longest(self.questions, answers):
                if q is None or q.content is None:
                    raise ValueError("Received answer without corresponding question.")
                if a is None or a.content is None:
                    raise ValueError("Received question without corresponding answer.")

                system_tag = a.system_tag(eos_token=eos_token) or ""
                qa_list.extend(
                    [
                        f"{QA_SPECIAL_TOKENS['Question']}{q.content}{eos_token}{system_tag}",
                        f"{QA_SPECIAL_TOKENS['Answer']}{a.content}{eos_token}",
                    ]
                )

            return qa_list

    @classmethod
    def from_strings(
        cls,
        questions: list[str],
        answers: list[str] | list[list[str]],
        context: Optional[str] = None,
        lang: Optional[str] = None,
        add_length: bool = True,
        property_dropout: float = SYSTEM_PROPERTY_DROP_PROBA,
    ):
        def length_indicator(s: str) -> int:
            return len(re.findall(r"\w+", s)) // 5 + 1

        if isinstance(answers[0], list):
            answers = [
                [
                    Utterance(content=a, length=length_indicator(a) if add_length else None, lang=lang, context=context)
                    for a in l
                ]
                for l in answers
            ]
        else:
            # todo: this does not yet support RM case
            answers = [
                Utterance(content=a, length=length_indicator(a) if add_length else None, lang=lang, context=context)
                for a in answers
            ]

        return cls(
            questions=[Utterance(content=q) for q in questions], answers=answers, property_dropout=property_dropout
        )

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
