import typing

import transformers


class Printer(typing.Protocol):
    def __call__(self, value: int) -> None:
        ...


# based on HF text streamer
class HFStreamer(transformers.generation.streamers.BaseStreamer):
    def __init__(self, input_ids: list[int], printer: Printer):
        self.input_ids = input_ids[::-1]
        self.printer = printer

    def put(self, value):
        if len(value.shape) > 1 and value.shape[0] > 1:
            raise ValueError("HFStreamer only supports batch size 1")
        elif len(value.shape) > 1:
            value = value[0]

        for token_id in value.tolist():
            if self.input_ids:
                input_id = self.input_ids.pop()
                print(f"input_id: {input_id}, token_id: {token_id}, match: {input_id == token_id}")
            else:
                self.printer(token_id)

    def end(self):
        pass
