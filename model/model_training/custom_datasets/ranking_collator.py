import random
from dataclasses import dataclass
from typing import Optional, Union

from transformers.tokenization_utils_base import PaddingStrategy, PreTrainedTokenizerBase, TruncationStrategy


@dataclass
class RankingDataCollator:
    """
    Data collator that will dynamically pad the inputs for multiple choice received.
    """

    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    random_offset_probability: Optional[float] = 0.5
    pad_to_multiple_of: Optional[int] = None

    def process_one(self, messages, return_length=False):
        messages = list(messages)

        if random.random() < self.random_offset_probability:
            truncation = TruncationStrategy.DO_NOT_TRUNCATE
            max_length = None
        else:
            truncation = TruncationStrategy.LONGEST_FIRST
            max_length = self.max_length

        # append eos token to each messages
        assert self.tokenizer.eos_token
        messages = [m + self.tokenizer.eos_token for m in messages]

        flatten_message = self.tokenizer(
            "".join(messages),
            max_length=max_length,
            truncation=truncation,
            return_offsets_mapping=True,
            padding=False,
        )

        if return_length:
            return min(len(flatten_message["input_ids"]), self.max_length)

    def __call__(self, features):
        flatten_features = []
        for pairs in features:
            for pos, neg in pairs:
                tokens = self.tokenizer(pos, truncation=True, max_length=self.max_length)
                neg_tokens = self.tokenizer(neg, truncation=True, max_length=self.max_length)
                tokens["pos_input_ids"] = tokens.pop("input_ids")
                tokens["pos_attention_mask"] = tokens.pop("attention_mask")
                tokens["neg_token_ids"] = neg_tokens["input_ids"]
                tokens["neg_attention_mask"] = neg_tokens["attention_mask"]
        batch = self.tokenizer.pad(
            flatten_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        if "token_type_ids" in batch:
            batch.pop("token_type_ids")
        return batch
