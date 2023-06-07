from dataclasses import dataclass
from typing import Optional, Union

from model_training.custom_datasets.formatting import DatasetEntryRm
from transformers.tokenization_utils_base import BatchEncoding, PaddingStrategy, PreTrainedTokenizerBase

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
    max_replies: Optional[int] = 5
    use_system_tag: bool = False
    system_property_dropout: float = 0.5
    system_add_length: bool = True

    def process_one(
        self,
        example: tuple[str | list[str] | None, list[str]] | DatasetEntryRm,
        return_length: int = False,
    ) -> list[BatchEncoding]:
        assert self.tokenizer.eos_token
        eos = self.tokenizer.eos_token

        if isinstance(example, DatasetEntryRm):
            prefix, replies = example.get_formatted(
                eos_token=eos,
                use_system_tag=self.use_system_tag,
                system_property_dropout=self.system_property_dropout,
                system_add_length=self.system_add_length,
                max_replies=self.max_replies,
            )
        else:
            messages, replies = example

            if self.max_replies:
                assert self.max_replies > 1, "max_replies parameter must be > 1 or None"
                if len(replies) > self.max_replies:
                    replies = replies[: self.max_replies]

            if messages is None or len(messages) == 1 and messages[0] is None:
                # special handling for non-dialogue datasets like Hellaswag
                prefix = ""
                replies = [r + eos for r in replies]
            else:
                # append eos token to each messages
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

    def __call__(
        self, examples: list[tuple[str | list[str] | None, list[str]]] | list[DatasetEntryRm]
    ) -> tuple[list[BatchEncoding], list[int]]:
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
        return batch, cu_lens
