import pydantic


class Settings(pydantic.BaseSettings):
    safety_model_name: str = "shahules786/blade2blade-t5-base"


settings = Settings()
