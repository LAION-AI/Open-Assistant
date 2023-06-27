from oasst_inference_server.models import DbChat, DbMessage, DbUser, DbWorker
from polyfactory.factories.pydantic_factory import ModelFactory


class DbChatFactory(ModelFactory[DbChat]):
    __model__ = DbChat

    @classmethod
    def title(cls) -> str:
        return cls.__faker__.sentence(nb_words=10, variable_nb_words=True)

    hidden: bool = False


class DbWorkerFactory(ModelFactory[DbWorker]):
    __model__ = DbWorker


class DbUserFactory(ModelFactory[DbUser]):
    __model__ = DbUser


class DbMessageFactory(ModelFactory[DbMessage]):
    __model__ = DbMessage

    work_parameters = None  # Work params lead to serialization errors if not none
