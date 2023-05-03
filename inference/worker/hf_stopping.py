import torch
from tokenizers import Tokenizer
from transformers import StoppingCriteria


# We could use a more efficient algorithm here but I don't think it matters too much
def contains_sequence(whole: list[int], subsequence: list[int]) -> bool:
    for i in range(len(whole) - len(subsequence) + 1):
        if whole[i : i + len(subsequence)] == subsequence:
            return True
    return False


class SequenceStoppingCriteria(StoppingCriteria):
    def __init__(
        self,
        tokenizer: Tokenizer,
        stop_texts: list[str],
        input_length: int,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.stop_texts = stop_texts
        self.tokenizer = tokenizer
        self.input_length = input_length

    def __call__(
        self,
        input_ids: torch.LongTensor,
        scores: torch.FloatTensor,
        **kwargs,
    ) -> bool:
        # Assumes batch size 1, sufficient for our use case
        generated_ids = input_ids[0, self.input_length :].tolist()
        stop_sequences_ids = [self.tokenizer.encode(text, add_special_tokens=False) for text in self.stop_texts]
        return any(contains_sequence(generated_ids, stop_sequence_ids) for stop_sequence_ids in stop_sequences_ids)
