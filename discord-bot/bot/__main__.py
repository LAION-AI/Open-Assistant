import logging
import os

import uvloop

from bot.bot import bot
from hikari.presences import Activity, ActivityType, Status

logger = logging.getLogger(__name__)

def main():
    if os.name != "nt":
        uvloop.install()

    logger.info("Starting bot")

    activity = Activity(
        name="/help",
        type=ActivityType.PLAYING,
    )
    status = Status.ONLINE

    try:
        bot.run(
            check_for_updates=True,
            activity=activity,
            status=status,
        )
    except Exception as e:
        logger.exception("Error starting bot: %s", e)

if __name__ == "__main__":
    main()
