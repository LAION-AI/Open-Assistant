import pydantic


class Settings(pydantic.BaseSettings):
    # HuggingFace model ID for the model to load in blade2blade
    safety_model_name: str = "shahules786/blade2blade-t5-base"


settings = Settings()
