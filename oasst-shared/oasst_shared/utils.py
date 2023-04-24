import time
from datetime import datetime, timezone
from functools import wraps

from loguru import logger

DELETED_USER_DISPLAY_NAME = "Deleted User"
DELETED_USER_ID_PREFIX = "deleted_"


def utcnow() -> datetime:
    """Return the current utc date and time with tzinfo set to UTC."""
    return datetime.now(timezone.utc)


def unaware_to_utc(d: datetime | None) -> datetime:
    """Set timezeno to UTC if datetime is unaware (tzinfo == None)."""
    if d and d.tzinfo is None:
        return d.replace(tzinfo=timezone.utc)
    return d


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class ScopeTimer:
    def __init__(self):
        self.start()

    def start(self) -> None:
        """Measure new start time"""
        self.start_time = time.perf_counter()

    def stop(self) -> float:
        """Store and return the elapsed time"""
        self.elapsed = time.perf_counter() - self.start_time
        return self.elapsed

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()


def log_timing(func=None, *, log_kwargs: bool = False, level: int | str = "DEBUG") -> None:
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            timer = ScopeTimer()
            result = func(*args, **kwargs)
            elapsed = timer.stop()
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
