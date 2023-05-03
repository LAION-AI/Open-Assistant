import torch
from tokenizers import Tokenizer
from transformers import StoppingCriteria


class SequenceStoppingCriteria(StoppingCriteria):
    def __init__(
        self,
        tokenizer: Tokenizer,
        stop_texts: list[str],
        input_prompt: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.stop_texts = stop_texts
        self.tokenizer = tokenizer
        self.input_length = len(tokenizer.encode(input_prompt)[0])

    def __call__(
        self,
        input_ids: torch.LongTensor,
        scores: torch.FloatTensor,
        **kwargs,
    ) -> bool:
        # Assumes batch size 1, sufficient for our use case
        generated_ids = input_ids[0, self.input_length :].tolist()
        # TODO: optimise this. Inefficient to decode whole sequence every time
        # but can't encode stop sequences as they don't always tokenize the same
        generated_text = self.tokenizer.decode(generated_ids)
        print("CHECKING STOP CRITERIA")
        print("Generated text:", generated_text)
        print("Stop texts:", str(self.stop_texts))
        print("Matches:", str([text for text in self.stop_texts if text in generated_text]))
        print("FINISHED CHECKING STOP CRITERIA")
        return any(text in generated_text for text in self.stop_texts)
