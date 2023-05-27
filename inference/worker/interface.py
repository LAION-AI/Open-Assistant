from typing import List, Optional, Union
import pydantic
from oasst_shared import schemas


class GenerateStreamParameters(pydantic.BaseModel):
    """
    Parameters for generating a stream.
    """

    max_new_tokens: int = 1024
    do_sample: bool = True
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    typical_p: Optional[float] = None
    temperature: Optional[float] = None
    repetition_penalty: Optional[float] = None
    seed: Optional[int] = None
    stop: List[str] = []
    details: bool = True
    plugins: List[schemas.inference.PluginEntry] = pydantic.Field(default_factory=list)

    @staticmethod
    def from_work_parameters(params: schemas.inference.WorkParameters) -> "GenerateStreamParameters":
        """
        Create GenerateStreamParameters instance from WorkParameters instance.

        Args:
            params: WorkParameters instance.

        Returns:
            GenerateStreamParameters instance.
        """
        return GenerateStreamParameters(
            max_new_tokens=params.sampling_parameters.max_new_tokens,
            do_sample=params.do_sample,
            top_k=params.sampling_parameters.top_k,
            top_p=params.sampling_parameters.top_p,
            typical_p=params.sampling_parameters.typical_p,
            temperature=params.sampling_parameters.temperature,
            repetition_penalty=params.sampling_parameters.repetition_penalty,
            seed=params.seed,
            plugins=params.plugins,
        )


class GenerateStreamRequest(pydantic.BaseModel):
    """
    Request to generate a stream.
    """

    inputs: str
    parameters: GenerateStreamParameters


class Token(pydantic.BaseModel):
    """
    Token information.
    """

    text: str
    logprob: Optional[float] = None
    id: int

    def __len__(self) -> int:
        """
        Return the length of the token text.

        Returns:
            Length of the token text.
        """
        return len(self.text)

    def to_token_response(self, request_id: str) -> schemas.inference.TokenResponse:
        """
        Convert Token instance to TokenResponse instance.

        Args:
            request_id: Request ID.

        Returns:
            TokenResponse instance.
        """
        return schemas.inference.TokenResponse(
            request_id=request_id,
            text=self.text,
            log_prob=self.logprob,
            token_id=self.id,
        )


class StreamDetails(pydantic.BaseModel):
    """
    Details of the generated stream.
    """

    generated_tokens: int
    seed: Optional[int] = None
    finish_reason: Optional[Literal["length", "eos_token", "stop_sequence"]] = None


class GenerateStreamResponse(pydantic.BaseModel):
    """
    Response from generating a stream.
    """

    token: Optional[Token] = None
    generated_text: Optional[str] = None
    details: Optional[StreamDetails] = None
    error: Optional[str] = None

    @property
    def is_end(self) -> bool:
        """
        Check if the generation is complete.

        Returns:
            True if generation is complete, False otherwise.
        """
        return self.generated_text is not None

    @property
    def is_error(self) -> bool:
        """
        Check if the response contains an error.

        Returns:
            True if the response contains an error, False otherwise.
        """
        return self.error is not None
