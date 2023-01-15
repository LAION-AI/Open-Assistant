import time
from datetime import datetime, timezone

from loguru import logger


def utcnow() -> datetime:
    """Return the current utc date and time with tzinfo set to UTC."""
    return datetime.now(timezone.utc)


def log_timing(func):
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
        return result

    return wrapped
