import pydantic


class Settings(pydantic.BaseSettings):
    backend_url: str = "ws://localhost:8000"
    model_id: str = "distilgpt2"
    inference_server_url: str = "http://localhost:8001"
    api_key: str = "0000"

    max_input_length: int = 1000
    max_total_tokens: int = 1512


settings = Settings()
