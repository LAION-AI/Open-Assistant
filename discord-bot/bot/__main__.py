# -*- coding: utf-8 -*-
"""Entry point for the bot."""
import logging
import os

from bot.bot import bot

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()

    logger.info("Starting bot")
    bot.run()
