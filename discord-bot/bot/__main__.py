"""Entry point for the bot."""
import logging
import os

from bot.bot import bot
from hikari.presences import Activity, ActivityType, Status

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    logger.info("Starting bot")
    bot.run(
        check_for_updates=True,
        activity=Activity(
            name="/help",
            type=ActivityType.PLAYING,
        ),
        status=Status.ONLINE,
    )
