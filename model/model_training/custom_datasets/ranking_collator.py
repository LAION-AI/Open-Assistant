from dataclasses import dataclass
from typing import Optional, Union

from transformers.tokenization_utils_base import PaddingStrategy, PreTrainedTokenizerBase

from .formatting import format_pairs, format_reply


@dataclass
class RankingDataCollator:
    """
    Data collator that will dynamically pad the inputs for multiple choice received.
    """

    tokenizer: PreTrainedTokenizerBase
    padding: Union[bool, str, PaddingStrategy] = True
    max_length: Optional[int] = None
    min_prefix_length: int = 256
    pad_to_multiple_of: Optional[int] = None

    def process_one(self, example, return_length=False):
        messages, replies = example

        # append eos token to each messages
        assert self.tokenizer.eos_token
        eos = self.tokenizer.eos_token
        prefix = "".join(format_pairs(messages, eos_token=eos))

        replies = [format_reply(r, eos_token=eos) for r in replies]

        prefix_tokens = self.tokenizer(prefix, padding=False, truncation=False)
        reply_tokens = [self.tokenizer(r, padding=False, truncation=False) for r in replies]

        prefix_len = len(prefix_tokens.input_ids)
        suffix_len = max(len(r.input_ids) for r in reply_tokens)
        if return_length:
            return min(prefix_len + suffix_len, self.max_length)

        for r in reply_tokens:
            max_prefix_len = (
                prefix_len
                if self.max_length is None
                else max(self.min_prefix_length, self.max_length - len(r.input_ids))
            )
            max_suffix_len = len(r.input_ids) if self.max_length is None else self.max_length - max_prefix_len

            for k in r.keys():
                r[k] = prefix_tokens[k][-max_prefix_len:] + r[k][:max_suffix_len]

        return reply_tokens

    def __call__(self, examples):
        flat_tokenized, cu_lens = [], [0]
        n_samples = 0
        for example in examples:
            tokenized = self.process_one(example)
            flat_tokenized.extend(tokenized)

            n_samples += len(tokenized)
            cu_lens.append(n_samples)

        batch = self.tokenizer.pad(
            flat_tokenized,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )

        if "token_type_ids" in batch:
            batch.pop("token_type_ids")
        return (batch, cu_lens)
