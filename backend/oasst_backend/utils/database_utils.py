from enum import IntEnum
from functools import wraps
from http import HTTPStatus
from typing import Callable

from loguru import logger
from oasst_backend.config import settings
from oasst_backend.database import engine
from oasst_shared.exceptions import OasstError, OasstErrorCode
from psycopg2.errors import DeadlockDetected, ExclusionViolation, SerializationFailure, UniqueViolation
from sqlalchemy.exc import OperationalError, PendingRollbackError
from sqlmodel import Session, SQLModel

"""
Error Handling Reference: https://www.postgresql.org/docs/15/mvcc-serialization-failure-handling.html
"""


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
"""


def managed_tx_method(auto_commit: CommitMode = CommitMode.COMMIT, num_retries=settings.DATABASE_MAX_TX_RETRY_COUNT):
    def decorator(f):
        @wraps(f)
        def wrapped_f(self, *args, **kwargs):
            try:
                result = None
                if auto_commit == CommitMode.COMMIT:
                    retry_exhausted = True
                    for i in range(num_retries):
                        try:
                            result = f(self, *args, **kwargs)
                            self.db.commit()
                            if isinstance(result, SQLModel):
                                self.db.refresh(result)
                            retry_exhausted = False
                            break
                        except PendingRollbackError as e:
                            logger.info(str(e))
                            self.db.rollback()
                        except OperationalError as e:
                            if e.orig is not None and isinstance(
                                e.orig, (SerializationFailure, DeadlockDetected, UniqueViolation, ExclusionViolation)
                            ):
                                logger.info(f"{type(e.orig)} Inner {e.orig.pgcode} {type(e.orig.pgcode)}")
                                self.db.rollback()
                            else:
                                raise e
                        logger.info(f"Retry {i+1}/{num_retries}")
                    if retry_exhausted:
                        raise OasstError(
                            "DATABASE_MAX_RETIRES_EXHAUSTED",
                            error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                            http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        )
                else:
                    result = f(self, *args, **kwargs)
                    if auto_commit == CommitMode.FLUSH:
                        self.db.flush()
                        if isinstance(result, SQLModel):
                            self.db.refresh(result)
                    elif auto_commit == CommitMode.ROLLBACK:
                        self.db.rollback()
                return result
            except Exception as e:
                logger.info(str(e))
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
                result = None
                if auto_commit == CommitMode.COMMIT:
                    retry_exhausted = True
                    for i in range(num_retries):
                        try:
                            result = await f(self, *args, **kwargs)
                            self.db.commit()
                            if isinstance(result, SQLModel):
                                self.db.refresh(result)
                            retry_exhausted = False
                            break
                        except PendingRollbackError as e:
                            logger.info(str(e))
                            self.db.rollback()
                        except OperationalError as e:
                            if e.orig is not None and isinstance(
                                e.orig, (SerializationFailure, DeadlockDetected, UniqueViolation, ExclusionViolation)
                            ):
                                logger.info(f"{type(e.orig)} Inner {e.orig.pgcode} {type(e.orig.pgcode)}")
                                self.db.rollback()
                            else:
                                raise e
                        logger.info(f"Retry {i+1}/{num_retries}")
                    if retry_exhausted:
                        raise OasstError(
                            "DATABASE_MAX_RETIRES_EXHAUSTED",
                            error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                            http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        )
                else:
                    result = await f(self, *args, **kwargs)
                    if auto_commit == CommitMode.FLUSH:
                        self.db.flush()
                        if isinstance(result, SQLModel):
                            self.db.refresh(result)
                    elif auto_commit == CommitMode.ROLLBACK:
                        self.db.rollback()
                return result
            except Exception as e:
                logger.info(str(e))
                raise e

        return wrapped_f

    return decorator


def default_session_factory() -> Session:
    return Session(engine)


def managed_tx_function(
    auto_commit: CommitMode = CommitMode.COMMIT,
    num_retries=settings.DATABASE_MAX_TX_RETRY_COUNT,
    session_factory: Callable[..., Session] = default_session_factory,
):
    """Passes Session object as first argument to wrapped function."""

    def decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                result = None
                if auto_commit == CommitMode.COMMIT:
                    retry_exhausted = True
                    for i in range(num_retries):
                        with session_factory() as session:
                            try:
                                result = f(session, *args, **kwargs)
                                session.commit()
                                if isinstance(result, SQLModel):
                                    session.refresh(result)
                                retry_exhausted = False
                                break
                            except PendingRollbackError as e:
                                logger.info(str(e))
                                session.rollback()
                            except OperationalError as e:
                                if e.orig is not None and isinstance(
                                    e.orig,
                                    (SerializationFailure, DeadlockDetected, UniqueViolation, ExclusionViolation),
                                ):
                                    logger.info(f"{type(e.orig)} Inner {e.orig.pgcode} {type(e.orig.pgcode)}")
                                    session.rollback()
                                else:
                                    raise e
                        logger.info(f"Retry {i+1}/{num_retries}")
                    if retry_exhausted:
                        raise OasstError(
                            "DATABASE_MAX_RETIRES_EXHAUSTED",
                            error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                            http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        )
                else:
                    with session_factory() as session:
                        result = f(session, *args, **kwargs)
                    if auto_commit == CommitMode.FLUSH:
                        session.flush()
                        if isinstance(result, SQLModel):
                            session.refresh(result)
                    elif auto_commit == CommitMode.ROLLBACK:
                        session.rollback()
                return result
            except Exception as e:
                logger.info(str(e))
                raise e

        return wrapped_f

    return decorator


def async_managed_tx_function(
    auto_commit: CommitMode = CommitMode.COMMIT,
    num_retries=settings.DATABASE_MAX_TX_RETRY_COUNT,
    session_factory: Callable[..., Session] = default_session_factory,
):
    """Passes Session object as first argument to wrapped function."""

    def decorator(f):
        @wraps(f)
        async def wrapped_f(*args, **kwargs):
            try:
                result = None
                if auto_commit == CommitMode.COMMIT:
                    retry_exhausted = True
                    for i in range(num_retries):
                        with session_factory() as session:
                            try:
                                result = await f(session, *args, **kwargs)
                                session.commit()
                                if isinstance(result, SQLModel):
                                    session.refresh(result)
                                retry_exhausted = False
                                break
                            except PendingRollbackError as e:
                                logger.info(str(e))
                                session.rollback()
                            except OperationalError as e:
                                if e.orig is not None and isinstance(
                                    e.orig,
                                    (SerializationFailure, DeadlockDetected, UniqueViolation, ExclusionViolation),
                                ):
                                    logger.info(f"{type(e.orig)} Inner {e.orig.pgcode} {type(e.orig.pgcode)}")
                                    session.rollback()
                                else:
                                    raise e
                        logger.info(f"Retry {i+1}/{num_retries}")
                    if retry_exhausted:
                        raise OasstError(
                            "DATABASE_MAX_RETIRES_EXHAUSTED",
                            error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                            http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        )
                else:
                    with session_factory() as session:
                        result = await f(session, *args, **kwargs)
                    if auto_commit == CommitMode.FLUSH:
                        session.flush()
                        if isinstance(result, SQLModel):
                            session.refresh(result)
                    elif auto_commit == CommitMode.ROLLBACK:
                        session.rollback()
                return result
            except Exception as e:
                logger.info(str(e))
                raise e

        return wrapped_f

    return decorator
