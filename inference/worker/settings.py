import pydantic


class Settings(pydantic.BaseSettings):
    backend_url: str = "ws://localhost:8000"
    model_id: str = "distilgpt2"
    inference_server_url: str = "http://localhost:8001"


settings = Settings()
