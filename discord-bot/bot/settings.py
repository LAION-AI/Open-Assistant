# -*- coding: utf-8 -*-
"""Configuration for the bot."""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Settings for the bot."""

    token: str = Field(env="TOKEN", default="")
    declare_global_commands: int = Field(env="DECLARE_GLOBAL_COMMANDS", default=0)
    owner_ids: list[int] = Field(env="OWNER_IDS", default_factory=list)
    prefix: str = Field(env="PREFIX", default="./")

    class Config(BaseSettings.Config):
        env_file = ".env"
