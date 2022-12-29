# -*- coding=utf-8 -*-
"""Configuration for the bot."""

import logging
from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration for the bot."""

    token: str
    declare_global_commands: int
    owner_ids: list[int]

    @classmethod
    def from_env(cls):
        token = getenv("TOKEN", None)

        if token is None:
            logger.error("Invalid token, please set the TOKEN environment variable.")
            exit(1)

        return cls(
            token=token,
            declare_global_commands=int(getenv("DECLARE_GLOBAL_COMMANDS", 0)),
            owner_ids=[int(x) for x in getenv("OWNER_IDS", "").split(",")],
        )
