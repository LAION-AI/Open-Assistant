# -*- coding: utf-8 -*-
from pydantic import AnyHttpUrl, BaseSettings


class BotSettings(BaseSettings):
    BACKEND_URL: AnyHttpUrl = "http://localhost:8080"
    API_KEY: str = "any_key"
    BOT_TOKEN: str
    BOT_CHANNEL_NAME: str = "bot"
    OWNER_ID: int = None
    TEMPLATE_DIR: str = "./templates"
    DEBUG: bool = True


settings = BotSettings(_env_file=".env")
