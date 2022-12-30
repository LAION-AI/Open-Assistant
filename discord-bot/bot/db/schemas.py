# -*- coding: utf-8 -*-
"""Database schemas."""
from aiosqlite import Row
from pydantic import BaseModel


class GuildSettings(BaseModel):
    """Guild settings."""

    guild_id: int
    log_channel_id: int | None

    @classmethod
    def parse_obj(cls, obj: Row) -> "GuildSettings":
        """Deserialize a Row object from aiosqlite into a GuildSettings object."""
        return cls(guild_id=obj[0], log_channel_id=obj[1])
