import torch
from tokenizers import Tokenizer
from transformers import StoppingCriteria


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
        new_input_ids = [i[self.input_length :] for i in input_ids.long().tolist()]

        stops = []
        for text in self.stop_texts:
            stop = []
            for input_id in new_input_ids:
                decoded = self.tokenizer.decode(input_id)
                stop.append(text in decoded)
            stops.append(all(stop))

        return any(stops)
