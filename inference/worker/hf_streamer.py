import typing

import transformers


class Printer(typing.Protocol):
    def __call__(self, value: int) -> None:
        ...


# based on HF text streamer
class HFStreamer(transformers.generation.streamers.BaseStreamer):
    def __init__(self, printer: Printer):
        self.printer = printer

    def put(self, value):
        if len(value.shape) > 1 and value.shape[0] > 1:
            raise ValueError("HFStreamer only supports batch size 1")
        elif len(value.shape) > 1:
            value = value[0]

        self.printer(value)

    def end(self):
        pass
