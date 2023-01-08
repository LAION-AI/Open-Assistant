import typing as t
from datetime import datetime

import hikari


def format_time(dt: datetime, fmt: t.Literal["t", "T", "D", "f", "F", "R"]) -> str:
    """Format a datetime object into the discord time format.

    ```
    | t | HH:MM            | 16:20
    | T | HH:MM:SS         | 16:20:11
    | D | D Mo Yr          | 20 April 2022
    | f | D Mo Yr HH:MM    | 20 April 2022 16:20
    | F | W, D Mo Yr HH:MM | Wednesday, 20 April 2022 16:20
    | R | relative         | in an hour
    ```
    """
    if fmt in ("t", "T", "D", "f", "F", "R"):
        return f"<t:{dt.timestamp():.0f}:{fmt}>"
    else:
        raise ValueError(f"`fmt` must be 't', 'T', 'D', 'f', 'F' or 'R', not {fmt}")


def mention(
    id: hikari.Snowflakeish,
    type: t.Literal["channel", "role", "user"],
) -> str:
    """Mention an object."""
    if type == "channel":
        return f"<#{id}>"
    elif type == "user":
        return f"<@{id}>"
    elif type == "role":
        return f"<@&{id}>"
    else:
        raise ValueError(f"`type` must be 'channel', 'user', or 'role', not {type}")
