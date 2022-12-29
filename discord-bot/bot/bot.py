# -*- coding=utf-8 -*-
"""Bot logic."""
import hikari

import aiosqlite
import lightbulb
import miru
from bot.config import Config

config = Config.from_env()

bot = lightbulb.BotApp(
    token=config.token,
    logs="DEBUG",
    prefix="./",
    default_enabled_guilds=config.declare_global_commands,
    owner_ids=config.owner_ids,
    intents=hikari.Intents.ALL,
)


@bot.listen()
async def on_starting(event: hikari.StartingEvent):
    """Setup."""

    miru.install(bot)  # component handler
    bot.load_extensions_from("./bot/extensions")  # load extensions

    bot.d.db = await aiosqlite.connect(":memory:")  # TODO: Update
    await bot.d.db.executescript(open("./bot/db/schema.sql").read())
    await bot.d.db.commit()


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent):
    """Cleanup."""
    await bot.d.db.close()
