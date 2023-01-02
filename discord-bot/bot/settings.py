# -*- coding: utf-8 -*-
"""Configuration for the bot."""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Settings for the bot."""

    bot_token: str = Field(env="BOT_TOKEN", default="")
    """Discord bot token."""
    declare_global_commands: int = Field(env="DECLARE_GLOBAL_COMMANDS", default=0)
    """Discord server ID to instantly have slash commands in."""
    owner_ids: list[int] = Field(env="OWNER_IDS", default_factory=list)
    """List of user IDs that can use owner-only commands."""
    prefix: str = Field(env="PREFIX", default="./")
    """Bot prefix."""
    oasst_api_url: str = Field(env="OASST_API_URL", default="http://localhost:8080")
    """OASST API url."""
    oasst_api_key: str = Field(env="OASST_API_KEY", default="")
    """OASST API key."""
    track_perf: bool = Field(env="TRACK_PERF", default=False)
    """Whether to track CPU/memory performance of the bot."""

    class Config(BaseSettings.Config):
        env_file = ".env"
        case_sensitive = False
