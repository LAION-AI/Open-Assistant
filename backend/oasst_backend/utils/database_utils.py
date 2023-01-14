from functools import wraps

from loguru import logger
from sqlalchemy.exc import OperationalError


def manage_class_db_transaction(flag=True, num_retries=3):
    def decorator(f):
        @wraps(f)
        def wrapped_f(self, *args, **kwargs):
            try:
                for i in range(num_retries):
                    try:
                        result = f(self, *args, **kwargs)
                        if flag:
                            self.db.commit()
                        else:
                            self.db.flush()
                        return result
                    except OperationalError:
                        self.db.rollback()
                        pass
                logger.exception("DATABASE_MAX_RETIRES_EXHAUSTED")
            except Exception as e:
                raise e

        return wrapped_f

    return decorator


def async_manage_class_db_transaction(flag=True, num_retries=3):
    def decorator(f):
        @wraps(f)
        async def wrapped_f(self, *args, **kwargs):
            try:
                for i in range(num_retries):
                    try:
                        result = await f(self, *args, **kwargs)
                        if flag:
                            self.db.commit()
                        else:
                            self.db.flush()
                        return result
                    except OperationalError:
                        self.db.rollback()
                        pass
                logger.exception("Seed data insertion failed")
            except Exception as e:
                raise e

        return wrapped_f

    return decorator


def manage_method_db_transaction(db, flag=True, num_retries=3):
    def decorator(f):
        @wraps(f)
        def wrapped_f(self, *args, **kwargs):
            try:
                for i in range(num_retries):
                    try:
                        result = f(self, *args, **kwargs)
                        if flag:
                            db.commit()
                        else:
                            db.flush()
                        return result
                    except OperationalError:
                        db.rollback()
                        pass
                raise Warning("DATABASE_MAX_RETIRES_EXHAUSTED")
            except Exception as e:
                raise e

        return wrapped_f

    return decorator
