"""Configuration for the bot."""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Settings for the bot."""

    bot_token: str = Field(env="BOT_TOKEN", default="")
    declare_global_commands: int = Field(env="DECLARE_GLOBAL_COMMANDS", default=0)
    owner_ids: list[int] = Field(env="OWNER_IDS", default_factory=list)
    prefix: str = Field(env="PREFIX", default="/")
    oasst_api_url: str = Field(env="OASST_API_URL", default="http://localhost:8080")
    oasst_api_key: str = Field(env="OASST_API_KEY", default="")

    class Config(BaseSettings.Config):
        env_file = ".env"
        case_sensitive = False
