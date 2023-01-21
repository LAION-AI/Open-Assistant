from enum import IntEnum
from functools import wraps
from http import HTTPStatus
from typing import Callable

from loguru import logger
from oasst_backend.config import settings
from oasst_backend.database import engine
from oasst_shared.exceptions import OasstError, OasstErrorCode
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel


class CommitMode(IntEnum):
    """
    Commit modes for the managed tx methods
    """

    NONE = 0
    FLUSH = 1
    COMMIT = 2
    ROLLBACK = 3


"""
* managed_tx_method and async_managed_tx_method methods are decorators functions
* to be used on class functions. It expects the Class to have a 'db' Session object
* initialised
* TODO: tx method decorator for non class methods
"""


def managed_tx_method(auto_commit: CommitMode = CommitMode.COMMIT, num_retries=settings.DATABASE_MAX_TX_RETRY_COUNT):
    def decorator(f):
        @wraps(f)
        def wrapped_f(self, *args, **kwargs):
            try:
                for i in range(num_retries):
                    try:
                        result = f(self, *args, **kwargs)
                        if auto_commit == CommitMode.COMMIT:
                            self.db.commit()
                        elif auto_commit == CommitMode.FLUSH:
                            self.db.flush()
                        elif auto_commit == CommitMode.ROLLBACK:
                            self.db.rollback()
                        if isinstance(result, SQLModel):
                            self.db.refresh(result)
                        return result
                    except OperationalError:
                        logger.info(f"Retry {i+1}/{num_retries} after possible DB concurrent update conflict.")
                        self.db.rollback()
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.error("DB Rollback Failure")
                raise e

        return wrapped_f

    return decorator


def async_managed_tx_method(
    auto_commit: CommitMode = CommitMode.COMMIT, num_retries=settings.DATABASE_MAX_TX_RETRY_COUNT
):
    def decorator(f):
        @wraps(f)
        async def wrapped_f(self, *args, **kwargs):
            try:
                for i in range(num_retries):
                    try:
                        result = await f(self, *args, **kwargs)
                        if auto_commit == CommitMode.COMMIT:
                            self.db.commit()
                        elif auto_commit == CommitMode.FLUSH:
                            self.db.flush()
                        elif auto_commit == CommitMode.ROLLBACK:
                            self.db.rollback()
                        if isinstance(result, SQLModel):
                            self.db.refresh(result)
                        return result
                    except OperationalError:
                        logger.info(f"Retry {i+1}/{num_retries} after possible DB concurrent update conflict.")
                        self.db.rollback()
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.exception("DB Rollback Failure")
                raise e

        return wrapped_f

    return decorator


def default_session_factor() -> Session:
    return Session(engine)


def managed_tx_function(
    auto_commit: CommitMode = CommitMode.COMMIT,
    num_retries=settings.DATABASE_MAX_TX_RETRY_COUNT,
    session_factory: Callable[..., Session] = default_session_factor,
):
    """Passes Session object as first argument to wrapped function."""

    def decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                for i in range(num_retries):
                    with session_factory() as session:
                        try:
                            result = f(session, *args, **kwargs)
                            if auto_commit == CommitMode.COMMIT:
                                session.commit()
                            elif auto_commit == CommitMode.FLUSH:
                                session.flush()
                            elif auto_commit == CommitMode.ROLLBACK:
                                session.rollback()
                            return result
                        except OperationalError:
                            logger.info(f"Retry {i+1}/{num_retries} after possible DB concurrent update conflict.")
                            session.rollback()
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.error("DB Rollback Failure")
                raise e

        return wrapped_f

    return decorator
