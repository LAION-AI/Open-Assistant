# -*- coding: utf-8 -*-
"""Guild settings."""
import hikari
import lightbulb
from aiosqlite import Connection

from bot.db.schemas import GuildSettings
from bot.utils import mention

plugin = lightbulb.Plugin("GuildSettings")
plugin.add_checks(lightbulb.guild_only)
plugin.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD))


@plugin.command
@lightbulb.command("settings", "Bot settings for the server.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def settings(_: lightbulb.SlashContext) -> None:
    """Bot settings for the server."""
    # This will never execute because it is a group
    pass


@settings.child
@lightbulb.command("get", "Get all the guild settings.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get(ctx: lightbulb.SlashContext) -> None:
    """Get one of or all the guild settings."""
    conn: Connection = ctx.bot.d.db
    assert ctx.guild_id is not None  # `guild_only` check

    async with conn.cursor() as cursor:
        # Get all settings
        await cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (ctx.guild_id,))
        row = await cursor.fetchone()

        if row is None:
            await ctx.respond("No settings found for this guild.")
            return

        guild_settings = GuildSettings.parse_obj(row)

        # Respond with all
        # TODO: Embed
        await ctx.respond(
            f"""\
**Guild Settings**
`log_channel`: {
mention(guild_settings.log_channel_id, "channel")
if guild_settings.log_channel_id else 'not set'}
"""
        )


@settings.child
@lightbulb.option("channel", "The channel to use.", hikari.TextableGuildChannel)
@lightbulb.command("log_channel", "Set the channel that the bot logs task and label completions in.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def log_channel(ctx: lightbulb.SlashContext) -> None:
    """Set the channel that the bot logs task and label completions in."""
    channel: hikari.TextableGuildChannel = ctx.options.channel
    conn: Connection = ctx.bot.d.db
    assert ctx.guild_id is not None  # `guild_only` check

    await ctx.respond(f"Setting `log_channel` to {channel.mention}.")

    async with conn.cursor() as cursor:
        await cursor.execute(
            "INSERT OR REPLACE INTO guild_settings (guild_id, log_channel_id) VALUES (?, ?)",
            (ctx.guild_id, channel.id),
        )

    await conn.commit()


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
