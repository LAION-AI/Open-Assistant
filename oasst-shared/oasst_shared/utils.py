import time
from datetime import datetime, timezone
from functools import wraps

from loguru import logger


def utcnow() -> datetime:
    """Return the current utc date and time with tzinfo set to UTC."""
    return datetime.now(timezone.utc)


def log_timing(func=None, *, log_kwargs: bool = False, level: int | str = "DEBUG") -> None:
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            elapsed = end - start
            if log_kwargs:
                kwargs = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
                logger.log(level, f"Function '{func.__name__}({kwargs})' executed in {elapsed:f} s")
            else:
                logger.log(level, f"Function '{func.__name__}' executed in {elapsed:f} s")
            return result

        return wrapped

    if func and callable(func):
        return decorator(func)
    return decorator
