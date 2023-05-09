import re
from itertools import zip_longest
from random import random, shuffle
from typing import Optional

from model_training.custom_datasets.entities import Mode
from pydantic import BaseModel, validator
from pydantic.fields import ModelField

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


def compute_length(s: str) -> int:
    return len(re.findall(r"\w+", s)) // 5 + 1


class PretrainDatasetEntry(BaseModel):
    text: str | None = None


class Utterance(BaseModel):
    text: str

    lang: str | None = None
    quality: float | None = None
    humor: float | None = None
    creativity: float | None = None
    context: str | None = None

    @validator("quality", "humor", "creativity")
    def between_0_1(cls, v, field: ModelField) -> float:
        if v is not None and not (0 <= v <= 1):
            raise ValueError(f"Field {field.name} must be between 0 and 1. Received: {v}")
        return v

    def system_tag(
        self,
        eos_token: str,
        enabled: bool = True,
        property_dropout: float = 0.0,
        add_length: bool = True,
    ) -> str:
        if not enabled:
            return ""

        properties: list[tuple[float | str]] = []
        for k, v in self.dict().items():
            if v is not None and k in ["lang", "quality", "humor", "creativity"]:
                properties.append((k, v))

        if add_length:
            properties.append(("length", compute_length(self.text)))

        shuffle(properties)

        # ensure that potentially multi-line conext field comes last
        if self.context:
            properties.append(("context", self.context))

        fragments: list[str] = []
        for k, v in properties:
            if random() < property_dropout:
                continue

            if isinstance(v, float):
                fragments.append(f"{k}: {v:0.1f}")
            elif isinstance(v, str):
                if not v.isspace():  # ignore whitespace-only values
                    fragments.append(f"{k}: {v}")
            else:
                fragments.append(f"{k}: {v}")

        content = "\n".join(fragments)
        return f"{QA_SPECIAL_TOKENS['System']}{content}\n{eos_token}"


class DatasetEntry(BaseModel):
    # For a dialouge with [Q1, A1, Q2, A2]
    # questions: [Q1, Q2]
    # answers: [A1, A2]
    questions: list[Utterance]
    answers: list[Utterance]

    # def _get_formatted_rm(self, eos_token: str, use_system: bool, property_dropout: float, max_replies: int = 5):
    #     if isinstance(self.answers[0], list):
    #         answers = self.answers[0]
    #     else:
    #         answers = self.answers
    #     assert len(answers) > 1 and max_replies > 1
    #     answers = answers[:max_replies]
    #     match len(self.questions):
    #         case 0:
    #             question = ""
    #             # todo: not sure if this case is correct but it is equivalent to current non-dataset entry behaviour
    #             answers = [f"{a}{eos_token}" for a in answers]
    #         case 1:
    #             # todo: how to handle different system tags for the answers since the tag should be part of the question
    #             # answer_system_tags = [a.system_tag(eos_token=eos_token, property_dropout=self.property_dropout) or "" for a in answers]
    #             system_tag = self.questions[0].system_tag(
    #                 eos_token=eos_token,
    #                 enabled=use_system,
    #                 property_dropout=self.property_dropout,
    #             )
    #             question = f"{QA_SPECIAL_TOKENS['Question']}{self.questions[0].context}{eos_token}{system_tag}"
    #             answers = [f"{QA_SPECIAL_TOKENS['Answer']}{a}{eos_token}" for a in answers]
    #         case _:
    #             # todo: implement, especially oasst actually needs this
    #             raise ValueError("Received more than one question in RM mode. This is unexpected. Aborting")
    #     return (question, answers)

    def get_formatted(
        self,
        mode: Mode,
        eos_token: str,
        use_system_tag: bool = True,
        system_property_dropout: float = 0.5,
        system_add_length: bool = True,
        **kwargs,
    ) -> str | list[str] | tuple[str, list[str]]:
        if mode == Mode.sft:
            qa_list: list[str] = []

            # check if this is a RM capable dataset (so it has multiple answers to the same question)
            # and if so, extract just the highest scoring answer
            answers: list[Utterance]
            if isinstance(self.answers[0], list):
                answers = [answer[0] for answer in self.answers]
            else:
                answers = self.answers

            for q, a in zip_longest(self.questions, answers):
                if q is None or q.text is None:
                    raise ValueError("Received answer without corresponding question.")
                if a is None or a.text is None:
                    raise ValueError("Received question without corresponding answer.")

                if use_system_tag:
                    system_tag = a.system_tag(
                        eos_token=eos_token,
                        property_dropout=system_property_dropout,
                        add_length=system_add_length,
                    )
                else:
                    system_tag = ""

                qa_list.extend(
                    [
                        f"{QA_SPECIAL_TOKENS['Question']}{q.text}{eos_token}{system_tag}",
                        f"{QA_SPECIAL_TOKENS['Answer']}{a.text}{eos_token}",
                    ]
                )

            return qa_list

        # TODO: These modes are not implemented yet

        # elif mode == Mode.rl:

        # elif mode == Mode.rm:

        else:
            raise RuntimeError(f"Unsupported mode: {mode}")

    @classmethod
    def from_strings(
        cls,
        questions: list[str],
        answers: list[str] | list[list[str]],
        context: Optional[str] = None,
        lang: Optional[str] = None,
    ):
        if isinstance(answers[0], list):
            answers = [[Utterance(text=a, lang=lang, context=context) for a in l] for l in answers]
        else:
            # todo: this does not yet support RM case
            answers = [Utterance(text=a, lang=lang, context=context) for a in answers]

        return cls(questions=[Utterance(text=q) for q in questions], answers=answers)


def format_pairs(
    pairs: list[str] | DatasetEntry,
    eos_token: str,
    add_initial_reply_token: str = False,
    mode: Mode | None = None,
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
