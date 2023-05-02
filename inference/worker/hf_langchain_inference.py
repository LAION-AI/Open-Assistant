import interface
import utils
from langchain.llms.base import LLM
from loguru import logger
from settings import settings


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

        http = utils.HttpClient(
            base_url=settings.inference_server_url,
            basic_auth_username=settings.basic_auth_username,
            basic_auth_password=settings.basic_auth_password,
        )

        response = http.post(
            "/generate",
            json=request.dict(),
        )

        try:
            response.raise_for_status()
        except Exception:
            logger.exception("Failed to get response from inference server")
            logger.error(f"Response: {response.text}")
            raise

        response_json = response.json()

        # remove stop sequences from the end of the generated text
        for stop_seq in stop:
            if stop_seq in response_json.generated_text:
                response_json.generated_text = response_json.generated_text[
                    : response_json.generated_text.index(stop_seq)
                ]

        return response_json.generated_text
