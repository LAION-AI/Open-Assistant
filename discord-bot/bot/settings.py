"""Configuration for the bot."""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Settings for the bot."""

    # Bot token obtained from the Discord Developer Portal
    bot_token: str = Field(env_var="BOT_TOKEN", default="", description="Bot token from Discord Developer Portal")

    # ID of the server where global commands are declared
    declare_global_commands: int = Field(env_var="DECLARE_GLOBAL_COMMANDS", default=0, description="ID of server where global commands are declared")

    # IDs of the bot owners
    owner_ids: List[int] = Field(env_var="OWNER_IDS", default_factory=list, description="IDs of bot owners")

    # Prefix for commands
    prefix: str = Field(env_var="PREFIX", default="/", description="Prefix for commands")

    # URL for the OASST API
    oasst_api_url: str = Field(env_var="OASST_API_URL", default="http://localhost:8080", description="URL for the OASST API")

    # API key for the OASST API
    oasst_api_key: str = Field(env_var="OASST_API_KEY", default="", description="API key for the OASST API")

    class Config(BaseSettings.Config):
        # Load environment variables from .env file
        env_file = ".env"
        # Make the settings case-insensitive
        case_sensitive = False
