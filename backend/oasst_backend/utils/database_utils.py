from enum import IntEnum
from functools import wraps
from http import HTTPStatus

from loguru import logger
from oasst_shared.exceptions import OasstError, OasstErrorCode
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel

MAX_DB_RETRY_COUNT = 3


class CommitMode(IntEnum):
    """
    Commit modes for the managed tx methods
    """

    NONE = 0
    FLUSH = 1
    COMMIT = 2


"""
* managed_tx_method and async_managed_tx_method methods are decorators functions
* to be used on class functions. It expects the Class to have a 'db' Session object
* initialised
* TODO: tx method decorator for non class methods
"""


def managed_tx_method(auto_commit: CommitMode = CommitMode.COMMIT, num_retries=MAX_DB_RETRY_COUNT):
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
                        if isinstance(result, SQLModel):
                            self.db.refresh(result)
                        return result
                    except OperationalError:
                        logger.info(f"Retrying count: {i+1} after possible db concurrent update conflict")
                        self.db.rollback()
                        pass
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.error("Db Rollback Failure")
                raise e

        return wrapped_f

    return decorator


def async_managed_tx_method(auto_commit: CommitMode = CommitMode.COMMIT, num_retries=MAX_DB_RETRY_COUNT):
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
                        if isinstance(result, SQLModel):
                            self.db.refresh(result)
                        return result
                    except OperationalError:
                        logger.info(f"Retrying count: {i+1} after possible db concurrent update conflict")
                        self.db.rollback()
                        pass
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.error("Db Rollback Failure")
                raise e

        return wrapped_f

    return decorator
