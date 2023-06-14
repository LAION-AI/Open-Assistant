import interface
import utils
from langchain.llms.base import LLM


class HFInference(LLM):
    """LangChain LLM implementation which uses the HF inference server configured in the worker settings."""

    max_new_tokens: int = 512
    top_k: int | None = None
    top_p: float | None = None
    typical_p: float | None = None
    temperature: float = 0.8
    repetition_penalty: float | None = None
    stop_sequences: list[str] = []
    seed: int = 42
    inference_server_url: str = ""

    @property
    def _llm_type(self) -> str:
        return "hf-inference"

    def _call(self, prompt: str, stop: list[str] | None = None) -> str:
        if stop is None:
            stop = self.stop_sequences
        else:
            stop += self.stop_sequences

        request = interface.GenerateStreamRequest(
            inputs=prompt,
            parameters=interface.GenerateStreamParameters(
                stop=stop,
                max_new_tokens=self.max_new_tokens,
                top_k=self.top_k,
                top_p=self.top_p,
                typical_p=self.typical_p,
                temperature=self.temperature,
                repetition_penalty=self.repetition_penalty,
                seed=self.seed,
            ),
        )

        for event in utils.get_inference_server_stream_events(request):
            stream_response = event

        generated_text = stream_response.generated_text or ""

        for stop_seq in stop:
            if stop_seq in generated_text:
                generated_text = generated_text[: generated_text.index(stop_seq)]

        return generated_text
