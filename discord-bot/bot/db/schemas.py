"""Database schemas."""
import typing as t

from aiosqlite import Connection, Row
from pydantic import BaseModel


class GuildSettings(BaseModel):
    """Guild settings."""

    guild_id: int
    log_channel_id: int | None

    @classmethod
    def parse_obj(cls, obj: Row) -> "GuildSettings":
        """Deserialize a Row object from aiosqlite into a GuildSettings object."""
        return cls(guild_id=obj[0], log_channel_id=obj[1])

    @classmethod
    async def from_db(cls, conn: Connection, guild_id: int) -> t.Optional["GuildSettings"]:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            if row is None:
                return None

            return cls.parse_obj(row)
