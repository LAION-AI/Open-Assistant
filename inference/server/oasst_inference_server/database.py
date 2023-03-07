import json
from pathlib import Path

import alembic.command
import alembic.config
import pydantic.json
from loguru import logger
from oasst_inference_server.schemas import chat as chat_schema
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


def default_json_serializer(obj):
    class_name = obj.__class__.__name__
    encoded = pydantic.json.pydantic_encoder(obj)
    encoded["_classname_"] = class_name
    return encoded


def custom_json_serializer(obj):
    return json.dumps(obj, default=default_json_serializer)


def custom_json_deserializer(s):
    d = json.loads(s)
    if not isinstance(d, dict):
        return d
    match d.get("_classname_"):
        case "WorkParameters":
            return inference.WorkParameters.parse_obj(d)
        case "WorkerConfig":
            return inference.WorkerConfig.parse_obj(d)
        case "MessageRequest":
            return chat_schema.MessageRequest.parse_obj(d)
        case "WorkRequest":
            return inference.WorkRequest.parse_obj(d)
        case "WorkResponsePacket":
            return inference.WorkResponsePacket.parse_obj(d)
        case None:
            return d
        case _:
            logger.error(f"Unknown class {d['_classname_']}")
            raise ValueError(f"Unknown class {d['_classname_']}")


def make_engine():
    engine = create_async_engine(
        settings.database_uri,
        json_serializer=custom_json_serializer,
        json_deserializer=custom_json_deserializer,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.db_echo,
        future=True,
    )
    return engine


db_engine = make_engine()


async def get_async_session(autoflush=True):
    async_session = sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False, autoflush=autoflush)
    async with async_session() as session:
        yield session


def alembic_upgrade(connection):
    alembic_ini_path = Path(__file__).parent.parent / "alembic.ini"
    alembic_cfg = alembic.config.Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_uri)
    alembic_cfg.attributes["connection"] = connection
    alembic.command.upgrade(alembic_cfg, "head")
