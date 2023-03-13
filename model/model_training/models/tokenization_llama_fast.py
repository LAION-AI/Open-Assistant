# Copyright 2020 Microsoft and the HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Fast Tokenization class for model DeBERTa."""

import os
from shutil import copyfile
from typing import Optional, Tuple

from transformers.file_utils import is_sentencepiece_available
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast
from transformers.utils import logging

if is_sentencepiece_available():
    from .tokenization_llama import LLaMATokenizer
else:
    LLaMATokenizer = None

logger = logging.get_logger(__name__)

VOCAB_FILES_NAMES = {"vocab_file": "tokenizer.model", "tokenizer_file": "tokenizer.json"}

PRETRAINED_VOCAB_FILES_MAP = {
    "vocab_file": {
        "decapoda-research/llama-7b-hf": "https://huggingface.co/decapoda-research/llama-7b-hf/resolve/main/tokenizer.model",
        "decapoda-research/llama-13b-hf": "https://huggingface.co/decapoda-research/llama-13b-hf/resolve/main/tokenizer.model",
        "decapoda-research/llama-30b-hf": "https://huggingface.co/decapoda-research/llama-33b-hf/resolve/main/tokenizer.model",
        "decapoda-research/llama-65b-hf": "https://huggingface.co/decapoda-research/llama-65b-hf/resolve/main/tokenizer.model",
    }
}
PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
    "decapoda-research/llama-7b-hf": 1000010,
    "decapoda-research/llama-13b-hf": 1000010,
    "decapoda-research/llama-30b-hf": 1000010,
    "decapoda-research/llama-65b-hf": 1000010,
}

PRETRAINED_INIT_CONFIGURATION = {
    "decapoda-research/llama-7b-hf": {"do_lower_case": False},
    "decapoda-research/llama-13b-hf": {"do_lower_case": False},
    "decapoda-research/llama-30b-hf": {"do_lower_case": False},
    "decapoda-research/llama-65b-hf": {"do_lower_case": False},
}


class LLaMATokenizerFast(PreTrainedTokenizerFast):
    r"""
    Constructs a LLaMa fast tokenizer. Based on [SentencePiece](https://github.com/google/sentencepiece).
    Args:
        vocab_file (`str`):
            [SentencePiece](https://github.com/google/sentencepiece) file (generally has a *.spm* extension) that
            contains the vocabulary necessary to instantiate a tokenizer.
        do_lower_case (`bool`, *optional*, defaults to `False`):
            Whether or not to lowercase the input when tokenizing.
        bos_token (`string`, *optional*, defaults to `"<s>"`):
            The beginning of sequence token that was used during pre-training. Can be used a sequence classifier token.
            When building a sequence using special tokens, this is not the token that is used for the beginning of
            sequence. The token used is the `cls_token`.
        eos_token (`string`, *optional*, defaults to `"</s>"`):
            The end of sequence token. When building a sequence using special tokens, this is not the token that is
            used for the end of sequence. The token used is the `sep_token`.
        unk_token (`str`, *optional*, defaults to `"<unk>"`):
            The unknown token. A token that is not in the vocabulary cannot be converted to an ID and is set to be this
            token instead.
        pad_token (`str`, *optional*, defaults to `"</s>"`):
            The token used for padding, for example when batching sequences of different lengths.
        sp_model_kwargs (`dict`, *optional*):
            Will be passed to the `SentencePieceProcessor.__init__()` method. The [Python wrapper for
            SentencePiece](https://github.com/google/sentencepiece/tree/master/python) can be used, among other things,
            to set:
            - `enable_sampling`: Enable subword regularization.
            - `nbest_size`: Sampling parameters for unigram. Invalid for BPE-Dropout.
              - `nbest_size = {0,1}`: No sampling is performed.
              - `nbest_size > 1`: samples from the nbest_size results.
              - `nbest_size < 0`: assuming that nbest_size is infinite and samples from the all hypothesis (lattice)
                using forward-filtering-and-backward-sampling algorithm.
            - `alpha`: Smoothing parameter for unigram sampling, and dropout probability of merge operations for
              BPE-dropout.
    """

    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
    pretrained_init_configuration = PRETRAINED_INIT_CONFIGURATION
    max_model_input_sizes = PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES
    slow_tokenizer_class = LLaMATokenizer

    def __init__(
        self,
        vocab_file=None,
        tokenizer_file=None,
        do_lower_case=False,
        split_by_punct=False,
        bos_token="<s>",
        eos_token="</s>",
        unk_token="<unk>",
        pad_token="</s>",
        **kwargs,
    ) -> None:
        super().__init__(
            vocab_file,
            tokenizer_file=tokenizer_file,
            do_lower_case=do_lower_case,
            bos_token=bos_token,
            eos_token=eos_token,
            pad_token=pad_token,
            unk_token=unk_token,
            split_by_punct=split_by_punct,
            **kwargs,
        )

        self.do_lower_case = do_lower_case
        self.split_by_punct = split_by_punct
        self.vocab_file = vocab_file
        self.can_save_slow_tokenizer = False if not self.vocab_file else True

    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        """
        Build model inputs from a sequence or a pair of sequence for sequence classification tasks by concatenating and
        adding special tokens. A DeBERTa sequence has the following format:
        - single sequence: [CLS] X [SEP]
        - pair of sequences: [CLS] A [SEP] B [SEP]
        Args:
            token_ids_0 (`List[int]`):
                List of IDs to which the special tokens will be added.
            token_ids_1 (`List[int]`, *optional*):
                Optional second list of IDs for sequence pairs.
        Returns:
            `List[int]`: List of [input IDs](../glossary#input-ids) with the appropriate special tokens.
        """

        if token_ids_1 is None:
            return [self.bos_token_id] + token_ids_0 + [self.eos_token_id]
        bos = [self.bos_token_id]
        eos = [self.eos_token_id]
        return bos + token_ids_0 + eos + bos + token_ids_1 + eos

    def get_special_tokens_mask(self, token_ids_0, token_ids_1=None, already_has_special_tokens=False):
        """
        Retrieves sequence ids from a token list that has no special tokens added. This method is called when adding
        special tokens using the tokenizer `prepare_for_model` or `encode_plus` methods.
        Args:
            token_ids_0 (`List[int]`):
                List of IDs.
            token_ids_1 (`List[int]`, *optional*):
                Optional second list of IDs for sequence pairs.
            already_has_special_tokens (`bool`, *optional*, defaults to `False`):
                Whether or not the token list is already formatted with special tokens for the model.
        Returns:
            `List[int]`: A list of integers in the range [0, 1]: 1 for a special token, 0 for a sequence token.
        """

        if already_has_special_tokens:
            return super().get_special_tokens_mask(
                token_ids_0=token_ids_0, token_ids_1=token_ids_1, already_has_special_tokens=True
            )

        if token_ids_1 is not None:
            return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]

    def create_token_type_ids_from_sequences(self, token_ids_0, token_ids_1=None):
        """
        Create a mask from the two sequences passed to be used in a sequence-pair classification task. A DeBERTa
        sequence pair mask has the following format:
        ```
        0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1
        | first sequence    | second sequence |
        ```
        If `token_ids_1` is `None`, this method only returns the first portion of the mask (0s).
        Args:
            token_ids_0 (`List[int]`):
                List of IDs.
            token_ids_1 (`List[int]`, *optional*):
                Optional second list of IDs for sequence pairs.
        Returns:
            `List[int]`: List of [token type IDs](../glossary#token-type-ids) according to the given sequence(s).
        """
        bos = [self.bos_token_id]
        eos = [self.eos_token_id]
        if token_ids_1 is None:
            return len(eos + token_ids_0 + bos) * [0]
        return len(bos + token_ids_0 + eos) * [0] + len(bos + token_ids_1 + eos) * [1]

    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        if not self.can_save_slow_tokenizer:
            raise ValueError(
                "Your fast tokenizer does not have the necessary information to save the vocabulary for a slow "
                "tokenizer."
            )

        if not os.path.isdir(save_directory):
            logger.error(f"Vocabulary path ({save_directory}) should be a directory")
            return
        out_vocab_file = os.path.join(
            save_directory, (filename_prefix + "-" if filename_prefix else "") + VOCAB_FILES_NAMES["vocab_file"]
        )

        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_file):
            copyfile(self.vocab_file, out_vocab_file)

        return (out_vocab_file,)
