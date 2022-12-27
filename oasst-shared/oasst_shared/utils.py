# -*- coding: utf-8 -*-
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current utc date and time with tzinfo set to UTC."""
    return datetime.now(timezone.utc)
