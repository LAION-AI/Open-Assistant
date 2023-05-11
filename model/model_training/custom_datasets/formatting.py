import re
from enum import Enum
from itertools import zip_longest
from random import random, shuffle
from typing import Literal, Optional

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


class Mode(str, Enum):
    sft = "sft"
    rm = "rm"
    rl = "rl"


class Role(str, Enum):
    prompter = "prompter"
    assistant = "assistant"


class Utterance(BaseModel):
    text: str
    role: Role
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
    pass


class PretrainDatasetEntry(DatasetEntry):
    text: str | None = None


class SftDatasetEntry(DatasetEntry):
    messages: list[Utterance]

    def get_formatted(
        self,
        eos_token: str,
        use_system_tag: bool = False,
        system_property_dropout: float = 0.5,
        system_add_length: bool = False,
    ) -> list[str]:
        output: list[str] = []

        for i, m in enumerate(self.messages):
            if m.role == Role.prompter:
                if use_system_tag and i + 1 < len(self.messages):
                    a = self.messages[i + 1]
                    assert a.role == Role.assistant
                    system_tag = a.system_tag(
                        eos_token=eos_token,
                        property_dropout=system_property_dropout,
                        add_length=system_add_length,
                    )
                else:
                    system_tag = ""
                output.append(f"{QA_SPECIAL_TOKENS['Question']}{m.text}{eos_token}{system_tag}")
            else:
                output.append(f"{QA_SPECIAL_TOKENS['Answer']}{m.text}{eos_token}")

        return output


def create_dataset_entry_qa(
    mode: Mode | Literal["sft", "rm", "rl"],
    questions: list[str],
    answers: list[str] | list[list[str]],
    context: Optional[str] = None,
    lang: Optional[str] = None,
) -> DatasetEntry:
    if mode == Mode.sft:
        messages: list[Utterance] = []

        for q, a in zip_longest(questions, answers):
            messages.append(Utterance(text=q, role=Role.prompter, lang=lang))
            if isinstance(a, list):
                a = a[0]
            messages.append(Utterance(text=a, role=Role.assistant, lang=lang, context=context))

        return SftDatasetEntry(messages=messages)
    else:
        raise RuntimeError("Unsupported mode")


def format_pairs(
    pairs: list[str] | SftDatasetEntry,
    eos_token: str,
    add_initial_reply_token: bool = False,
) -> list[str]:
    if isinstance(pairs, SftDatasetEntry):
        return pairs.get_formatted(eos_token=eos_token)
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
