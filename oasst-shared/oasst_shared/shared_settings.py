import pydantic


class SharedSettings(pydantic.BaseSettings):
    default_model_name: str = "_lorem"


shared_settings = SharedSettings()
