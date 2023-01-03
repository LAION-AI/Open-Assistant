from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import torch
from torch.nn import functional as F
from transformers.tokenization_utils_base import PaddingStrategy, PreTrainedTokenizerBase


@dataclass
class DialogueDataCollator:
    """
    Expects a list of texts corresponding to a sequence of [question, answer, question, answer, ...] pairs.
    """

    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None

    def __call__(self, features):
        # TODO add special tokens for question and answer here
        # additional_special_tokens = ['<question>', '<answer>']
        prompt_tokens = ["Question: ", "Answer: "]

        flatten_messages = []
        label_masks = []

        for messages in features:
            assert len(messages) % 2 == 0, "Number of messages must be even"
            messages = [
                (prompt_tokens[0] if i % 2 == 0 else "") + x + ((" " + prompt_tokens[1]) if i % 2 == 0 else "")
                for i, x in enumerate(messages)
            ]

            # Add a way for the model to terminate generation, reinitialize prompter
            messages.append(prompt_tokens[0])

            flatten_messages.append(
                self.tokenizer(
                    "".join(messages),
                    truncation=True,
                    max_length=self.max_length,
                    return_offsets_mapping=True,
                )
            )

            message_change_indices = np.cumsum([len(x) for x in messages[:-1]])
            # for each token an integer indicating the index of the message it belongs to. Just to create the label mask.
            # TEXT:             Question: Hello, how are you? Answer: I am fine. Question: What is your name? Answer: My name is John.
            # MESSAGE_INDICES:  0         0      0   0   0    0       1 1  1     2         2    2  2    2     2       3  3    3  3

            # If no result in next, we are predicting the last termination token(s)
            message_indices = list(
                map(
                    lambda x: next((i for i, val in enumerate(message_change_indices) if val >= x), -2),
                    list(map(lambda x: x[1], flatten_messages[-1]["offset_mapping"])),
                )
            )
            label_mask = np.roll(list(map(lambda x: x % 2 == 1, message_indices)), -1, -1)
            try:
                label_mask[[i for i in range(len(message_indices)) if message_indices[i] == -2][0] - 1] = True
            except IndexError:
                # an aftermath of padding
                pass

            label_masks.append(label_mask)
            flatten_messages[-1].pop("offset_mapping")

        batch = self.tokenizer.pad(
            flatten_messages,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        dim = batch["input_ids"].shape[-1]

        batch["label_masks"] = torch.stack([F.pad(torch.tensor(x), (0, dim - len(x))) for x in label_masks])

        for k in list(batch.keys()):
            if k not in ["input_ids", "attention_mask", "label_masks"]:
                batch.pop(k)

        return batch
