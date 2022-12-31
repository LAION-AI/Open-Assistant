# -*- coding: utf-8 -*-
"""Bot logic."""
import aiosqlite
import hikari
import lightbulb
import miru
from bot.api_client import OasstApiClient
from bot.settings import Settings

settings = Settings()

# TODO: Revisit cache settings
bot = lightbulb.BotApp(
    token=settings.bot_token,
    logs="DEBUG",
    prefix=settings.prefix,
    default_enabled_guilds=settings.declare_global_commands,
    owner_ids=settings.owner_ids,
    intents=hikari.Intents.ALL,
)


@bot.listen()
async def on_starting(event: hikari.StartingEvent):
    """Setup."""
    miru.install(bot)  # component handler
    bot.load_extensions_from("./bot/extensions")  # load extensions

    bot.d.db = await aiosqlite.connect("./bot/db/database.db")
    await bot.d.db.executescript(open("./bot/db/schema.sql").read())
    await bot.d.db.commit()

    bot.d.oasst_api = OasstApiClient(settings.oasst_api_url, settings.oasst_api_key)


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent):
    """Cleanup."""
    await bot.d.db.close()
    await bot.d.oasst_api.close()
