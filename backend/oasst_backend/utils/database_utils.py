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
                    except OperationalError as e:
                        if e.orig is not None and isinstance(
                            e.orig, (SerializationFailure, DeadlockDetected, UniqueViolation, ExclusionViolation)
                        ):
                            logger.info(f"{type(e.orig)} Inner {e.orig.pgcode} {type(e.orig.pgcode)}")
                            if auto_commit != CommitMode.COMMIT:
                                logger.info(
                                    "Since it is a flush or rollback, let the outer call handle the transaction retry"
                                )
                                # TODO: Is returning result ok ?
                                return result
                        else:
                            logger.info(f"Other kind of error {e}")
                            OasstError(
                                "DATABASE_OPERATION_ERROR",
                                error_code=OasstErrorCode.DATABASE_OPERATION_ERROR,
                                http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                            )
                    except PendingRollbackError as e:
                        logger.info(f"Retry {i+1}/{num_retries} after {e}")
                        self.db.rollback()
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.error(f"DB Failure {type(e)} {e}")
                OasstError(
                    "DATABASE_OPERATION_ERROR",
                    error_code=OasstErrorCode.DATABASE_OPERATION_ERROR,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )

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
                    except OperationalError as e:
                        if e.orig is not None and isinstance(
                            e.orig, (SerializationFailure, DeadlockDetected, UniqueViolation, ExclusionViolation)
                        ):
                            logger.info(f"{type(e.orig)} Inner {e.orig.pgcode} {type(e.orig.pgcode)}")
                            if auto_commit != CommitMode.COMMIT:
                                logger.info(
                                    "Since it is a flush or rollback, let the outer call handle the transaction retry"
                                )
                                # TODO: Is returning result ok ?
                                return result
                        else:
                            logger.info(f"Other kind of error {e}")
                            OasstError(
                                "DATABASE_OPERATION_ERROR",
                                error_code=OasstErrorCode.DATABASE_OPERATION_ERROR,
                                http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                            )
                    except PendingRollbackError as e:
                        logger.info(f"Retry {i+1}/{num_retries} after {e}")
                        self.db.rollback()
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.error(f"DB Failure {type(e)} {e}")
                OasstError(
                    "DATABASE_OPERATION_ERROR",
                    error_code=OasstErrorCode.DATABASE_OPERATION_ERROR,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )

        return wrapped_f

    return decorator


def default_session_factor() -> Session:
    return Session(engine)


def managed_tx_function(
    auto_commit: CommitMode = CommitMode.COMMIT,
    num_retries=settings.DATABASE_MAX_TX_RETRY_COUNT,
    session_factory: Callable[..., Session] = default_session_factor,
    refresh_result: bool = True,
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
                            if refresh_result and isinstance(result, SQLModel):
                                session.refresh(result)
                            return result
                        except OperationalError as e:
                            if e.orig is not None and isinstance(
                                e.orig, (SerializationFailure, DeadlockDetected, UniqueViolation, ExclusionViolation)
                            ):
                                logger.info(f"{type(e.orig)} Inner {e.orig.pgcode} {type(e.orig.pgcode)}")
                                if auto_commit != CommitMode.COMMIT:
                                    logger.info(
                                        "Since it is a flush or rollback, let the outer call handle the transaction retry"
                                    )
                                    # TODO: Is returning result ok ?
                                    return result
                            else:
                                logger.info(f"Other kind of error {e}")
                                OasstError(
                                    "DATABASE_OPERATION_ERROR",
                                    error_code=OasstErrorCode.DATABASE_OPERATION_ERROR,
                                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                                )
                        except PendingRollbackError as e:
                            logger.info(f"Retry {i+1}/{num_retries} after {e}")
                            session.rollback()
                raise OasstError(
                    "DATABASE_MAX_RETIRES_EXHAUSTED",
                    error_code=OasstErrorCode.DATABASE_MAX_RETRIES_EXHAUSTED,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            except Exception as e:
                logger.error(f"DB Failure {type(e)} {e}")
                OasstError(
                    "DATABASE_OPERATION_ERROR",
                    error_code=OasstErrorCode.DATABASE_OPERATION_ERROR,
                    http_status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )

        return wrapped_f

    return decorator
