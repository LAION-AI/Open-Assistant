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
        flatten_messages = []
        label_masks = []

        for messages in features:
            messages = list(messages)

            # Add a way for the model to terminate generation
            # When we predict the start of a new expected question, we want to be able to stop generation
            messages.append(self.tokenizer.eos_token)

            flatten_message = self.tokenizer(
                "".join(messages),
                truncation=True,
                max_length=self.max_length,
                return_offsets_mapping=True,
            )

            message_change_indices = np.cumsum([len(x) for x in messages[:-1]])
            # for each token an integer indicating the index of the message it belongs to. Just to create the label mask.
            # Label mask is true when predicting a token that is part of the answer, false otherwise.
            # TEXT:             Question: Hello, how are you? Answer: I am fine. Question: What is your name? Answer: My name is John. Question:
            # MESSAGE_INDICES:  0         0      0   0   0    0       1 1  1     2         2    2  2    2     2       3  3    3  3     -2
            # LABEL_MASK:       0         0      0   0   0    1       1 1  1     0         0    0  0    0     1       1  1    1  1     0

            # If no result in next, we are predicting the last termination token(s)
            message_indices = list(
                map(
                    lambda x: next((i for i, val in enumerate(message_change_indices) if val >= x), -2),
                    list(map(lambda x: x[1], flatten_message["offset_mapping"])),
                )
            )
            label_mask = np.roll(list(map(lambda x: x % 2 == 1, message_indices)), -1, -1)
            try:
                label_mask[[i for i in range(len(message_indices)) if message_indices[i] == -2][0] - 1] = True
            except IndexError:
                # due to truncation, we might not have the last termination token
                label_mask[-1] = False

            label_masks.append(label_mask)

            flatten_messages.append({k: v for k, v in flatten_message.items() if k != "offset_mapping"})

        batch = self.tokenizer.pad(
            flatten_messages,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        dim = batch["input_ids"].shape[-1]

        batch["label_masks"] = torch.stack(
            [F.pad(torch.tensor(x), (0, dim - len(x)), value=False) for x in label_masks]
        )
        batch["targets"] = torch.roll(batch["input_ids"], -1, -1)

        return batch
