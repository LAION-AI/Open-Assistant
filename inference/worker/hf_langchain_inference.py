from langchain.llms.base import LLM
from text_generation import Client


class HFInference(LLM):
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

        print(stop)
        client = Client(self.inference_server_url, timeout=1000)
        res = client.generate(
            prompt,
            stop_sequences=stop,
            max_new_tokens=self.max_new_tokens,
            top_k=self.top_k,
            top_p=self.top_p,
            typical_p=self.typical_p,
            temperature=self.temperature,
            repetition_penalty=self.repetition_penalty,
            seed=self.seed,
        )
        # remove stop sequences from the end of the generated text
        for stop_seq in stop:
            if stop_seq in res.generated_text:
                res.generated_text = res.generated_text[: res.generated_text.index(stop_seq)]

        return res.generated_text
