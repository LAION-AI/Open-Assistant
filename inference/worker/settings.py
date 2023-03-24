import pydantic


class Settings(pydantic.BaseSettings):
    backend_url: str = "ws://localhost:8000"
    model_config_name: str = "distilgpt2"
    inference_server_url: str = "http://localhost:8001"
    api_key: str = "0000"

    oa_protocol_version: str = "v2"

    retry_on_error: bool = True
    hf_pause: float = 0.075
    max_parallel_requests: int = 1
    use_stop_sequences: bool = False

    perform_oom_test: bool = False
    oom_test_max_length: int | None = None


settings = Settings()
