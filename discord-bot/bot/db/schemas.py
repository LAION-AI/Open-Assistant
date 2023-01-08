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
        """Retrieve the guild settings for the given guild ID from the database.

        Returns:
            The guild settings for the given guild ID, or None if no such settings are found.
        """
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            if row is None:
                return None

            return cls.parse_obj(row)

    async def save(self, conn: Connection) -> None:
        """Save the guild settings to the database."""
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO guild_settings (guild_id, log_channel_id) VALUES (?, ?) "
                "ON CONFLICT (guild_id) DO UPDATE SET log_channel_id = ?",
                (self.guild_id, self.log_channel_id, self.log_channel_id),
            )
