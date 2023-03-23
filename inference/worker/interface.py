from typing import Literal

import pydantic
from oasst_shared.schemas import inference


class GenerateStreamParameters(pydantic.BaseModel):
    max_new_tokens: int = 1024
    do_sample: bool = True
    top_k: int | None
    top_p: float | None
    typical_p: float | None
    temperature: float | None
    repetition_penalty: float | None
    seed: int | None
    stop: list[str] = []
    details: bool = True

    @staticmethod
    def from_work_parameters(params: inference.WorkParameters) -> "GenerateStreamParameters":
        return GenerateStreamParameters(
            max_new_tokens=params.sampling_parameters.max_new_tokens,
            do_sample=params.do_sample,
            top_k=params.sampling_parameters.top_k,
            top_p=params.sampling_parameters.top_p,
            typical_p=params.sampling_parameters.typical_p,
            temperature=params.sampling_parameters.temperature,
            repetition_penalty=params.sampling_parameters.repetition_penalty,
            seed=params.seed,
        )


class GenerateStreamRequest(pydantic.BaseModel):
    inputs: str
    parameters: GenerateStreamParameters


class Token(pydantic.BaseModel):
    text: str
    logprob: float | None
    id: int

    def __len__(self) -> int:
        return len(self.text)

    def to_token_response(self, request_id: str) -> inference.TokenResponse:
        return inference.TokenResponse(
            request_id=request_id,
            text=self.text,
            log_prob=self.logprob,
            token_id=self.id,
        )


class StreamDetails(pydantic.BaseModel):
    generated_tokens: int
    seed: int | None
    finish_reason: Literal["length", "eos_token", "stop_sequence"]


class GenerateStreamResponse(pydantic.BaseModel):
    token: Token | None
    generated_text: str | None
    details: StreamDetails | None
    error: str | None

    @property
    def is_end(self) -> bool:
        return self.generated_text is not None

    @property
    def is_error(self) -> bool:
        return self.error is not None
