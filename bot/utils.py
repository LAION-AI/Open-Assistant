# -*- coding: utf-8 -*-
import enum
import subprocess
from datetime import datetime

import pytz


def get_git_head_hash():
    # get current git hash
    x = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, universal_newlines=True)
    if x.returncode == 0:
        return x.stdout.replace("\n", "")
    return None


def utcnow() -> datetime:
    return datetime.now(pytz.UTC)


class DiscordTimestampStyle(str, enum.Enum):
    """
    Timestamp Styles

    t	16:20	                        Short Time
    T	16:20:30	                    Long Time
    d	20/04/2021	                    Short Date
    D	20 April 2021	                Long Date
    f *	20 April 2021 16:20	            Short Date/Time
    F	Tuesday, 20 April 2021 16:20	Long Date/Time
    R	2 months ago	                Relative Time

    See https://discord.com/developers/docs/reference#message-formatting-timestamp-styles
    """

    default = ""
    short_time = "t"
    long_time = "T"
    short_date = "d"
    long_date = "D"
    short_date_time = "f"
    long_date_time = "F"
    relative_time = "R"


def discord_timestamp(d: datetime, style: DiscordTimestampStyle = DiscordTimestampStyle.default):
    parts = ["<t:", str(int(d.timestamp()))]
    if style:
        parts.append(":")
        parts.append(style)
    parts.append(">")
    return "".join(parts)
