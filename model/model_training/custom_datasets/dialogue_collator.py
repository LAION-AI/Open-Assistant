import random
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import torch
from model_training.custom_datasets.formatting import (
    QA_SPECIAL_TOKENS,
    DatasetEntry,
    Mode,
    PretrainDatasetEntry,
    format_pairs,
    format_system_prefix,
)
from torch.nn import functional as F
from transformers.tokenization_utils_base import PaddingStrategy, PreTrainedTokenizerBase, TruncationStrategy


@dataclass
class DialogueDataCollator:
    """
    Expects a list of texts corresponding to a sequence of [question, answer, question, answer, ...] pairs.
    """

    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    mix_length_threshold: Optional[int] = 256
    mix_probability: Optional[float] = 0.6
    pad_to_multiple_of: Optional[int] = None
    samples_mixing: Optional[bool] = False
    random_offset_probability: Optional[float] = 0.5
    label_masking: bool = True
    use_system_prefix: bool = False
    system_prefix: str = None

    def __post_init__(self):
        assert self.tokenizer.eos_token

        if self.use_system_prefix:
            assert self.system_prefix
            self.system_prefix = self.tokenizer.encode(
                format_system_prefix(self.system_prefix, self.tokenizer.eos_token),
                add_special_tokens=False,
                return_tensors="np",
            )[0]
            self.max_length = self.max_length - len(self.system_prefix)

    def process_one(self, messages, return_length=False):
        total_short_context_one = 0
        if random.random() < self.random_offset_probability:
            truncation = TruncationStrategy.DO_NOT_TRUNCATE
            max_length = None
        else:
            truncation = TruncationStrategy.LONGEST_FIRST
            max_length = self.max_length

        pretrain_dataset = False
        if isinstance(messages, DatasetEntry):
            messages = messages.get_formatted(mode=Mode.sft, eos_token=self.tokenizer.eos_token)
        elif isinstance(messages, PretrainDatasetEntry):
            messages = messages.text
            pretrain_dataset = True
        else:
            messages = list(messages)
            messages = format_pairs(messages, self.tokenizer.eos_token)

        flatten_message = self.tokenizer(
            "".join(messages),
            max_length=max_length,
            truncation=truncation,
            padding=False,
        )

        if pretrain_dataset:
            label_mask = np.ones(len(flatten_message.input_ids), dtype=bool)
            return flatten_message, label_mask, 0

        if return_length:
            return min(len(flatten_message.input_ids), self.max_length)

        message_indices: Optional[list[int]] = None
        system_token_present = False
        if self.label_masking:
            # message_change_indices = np.cumsum([len(x) for x in messages])
            # for each token an integer indicating the index of the message it belongs to. Just to create the label mask.
            # Label mask is true when predicting a token that is part of the answer, false otherwise.
            # TEXT:             Question: Hello, how are you? Answer: I am fine. Question: What is your name? Answer: My name is John.
            # MESSAGE_INDICES:  0         0      0   0   0    1       1 1  1     2         2    2  2    2     3       3  3    3  3
            # LABEL_MASK:       0         0      0   0   0    1       1 1  1     0         0    0  0    0     1       1  1    1  1

            # If no result in next, we are predicting the last termination token(s)
            # message_indices = list(
            #     map(
            #         lambda x: next((i for i, val in enumerate(message_change_indices) if val >= x)),
            #         list(map(lambda x: x[1], flatten_message.offset_mapping)),
            #     )
            # )

            prompter_token_id = self.tokenizer.convert_tokens_to_ids(QA_SPECIAL_TOKENS["Question"])
            assistant_token_id = self.tokenizer.convert_tokens_to_ids(QA_SPECIAL_TOKENS["Answer"])
            system_token_id = self.tokenizer.convert_tokens_to_ids(QA_SPECIAL_TOKENS["System"])
            assert prompter_token_id >= 0 and assistant_token_id >= 0 and system_token_id >= 0

            message_indices = []
            i = -1
            # assume that system token is the very first token
            system_token_present = flatten_message.input_ids[0] == system_token_id
            for x in flatten_message.input_ids:
                if x in (prompter_token_id, assistant_token_id, system_token_id):
                    i += 1
                message_indices.append(i)

        input_length = len(flatten_message.input_ids)
        if self.max_length and input_length > self.max_length:
            offset = random.randint(0, input_length - self.max_length)
            for k in flatten_message.keys():
                v = flatten_message[k]
                if isinstance(v, list) and len(v) == input_length:
                    flatten_message[k] = v[offset : offset + self.max_length]
            if message_indices:
                message_indices = message_indices[offset : offset + self.max_length]

        if self.label_masking:
            if system_token_present:
                # assume system is before first prompter token
                label_mask = np.array([(idx > 0) and (idx % 2 == 0) for idx in message_indices])
            else:
                label_mask = np.array(list(map(lambda x: x % 2 == 1, message_indices)))
        else:
            label_mask = np.ones(len(flatten_message.input_ids), dtype=bool)

        label_mask[-1] = False  # make sure last token is inactive, has an effect only when truncating

        if len(flatten_message.input_ids) < self.mix_length_threshold and self.samples_mixing:
            total_short_context_one += len(flatten_message.input_ids)

        return {k: v for k, v in flatten_message.items() if k != "offset_mapping"}, label_mask, total_short_context_one

    def __call__(self, features):
        flatten_messages = []
        label_masks = []
        total_short_context = 0
        for messages in features:
            flatten_message, label_mask, total_short_context_one = self.process_one(messages)
            flatten_messages.append(flatten_message)
            label_masks.append(label_mask)
            total_short_context += total_short_context_one

        # packing
        if total_short_context > 2 and self.samples_mixing:
            _flatten_messages, _label_masks = [], []
            prev_short_msg, prev_short_mask = None, None
            for flatten_msg, label_mask in zip(flatten_messages, label_masks):
                if len(flatten_msg.input_ids) < self.mix_length_threshold and random.random() > self.mix_probability:
                    if prev_short_msg is not None:
                        for key in flatten_msg.keys():
                            flatten_msg[key] += prev_short_msg[key]
                            flatten_msg[key] = flatten_msg[key][: self.max_length]
                        label_mask = np.concatenate([label_mask, prev_short_mask])
                        _label_masks.append(label_mask[: self.max_length])
                        _flatten_messages.append(flatten_msg)
                        # reset
                        prev_short_msg, prev_short_mask = None, None
                    else:
                        # prime
                        prev_short_msg, prev_short_mask = flatten_msg, label_mask
                else:
                    _label_masks.append(label_mask)
                    _flatten_messages.append(flatten_msg)
            if prev_short_msg is not None:
                for key in flatten_msg.keys():
                    flatten_msg[key] += prev_short_msg[key]
                    flatten_msg[key] = flatten_msg[key][: self.max_length]
                label_mask = np.concatenate([label_mask, prev_short_mask])[: self.max_length]
                _label_masks.append(label_mask)
                _flatten_messages.append(flatten_msg)

            label_masks = _label_masks
            flatten_messages = _flatten_messages

        if self.use_system_prefix:
            flatten_messages = [
                {
                    "input_ids": np.concatenate([self.system_prefix, flatten_msg["input_ids"]]),
                    "attention_mask": np.concatenate(
                        [np.ones_like(self.system_prefix).astype(bool), flatten_msg["attention_mask"]]
                    ),
                }
                for flatten_msg in flatten_messages
            ]
            label_masks = [
                np.concatenate([np.zeros_like(self.system_prefix).astype(bool), label_mask])
                for label_mask in label_masks
            ]

        batch = self.tokenizer.pad(
            flatten_messages,
            padding=self.padding,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        dim = batch.input_ids.shape[-1]

        batch["label_masks"] = torch.stack(
            [F.pad(torch.tensor(x), (0, dim - len(x)), value=False) for x in label_masks]
        )
        batch["targets"] = torch.roll(batch.input_ids, -1, -1)

        return batch
