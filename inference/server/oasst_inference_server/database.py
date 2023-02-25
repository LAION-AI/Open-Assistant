import json

import pydantic.json
import sqlmodel
from loguru import logger
from oasst_inference_server import models
from oasst_inference_server.settings import settings


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
            return models.inference.WorkParameters.parse_obj(d)
        case "WorkerConfig":
            return models.inference.WorkerConfig.parse_obj(d)
        case "MessageRequest":
            return models.interface.MessageRequest.parse_obj(d)
        case "WorkRequest":
            return models.inference.WorkRequest.parse_obj(d)
        case "WorkResponsePacket":
            return models.inference.WorkResponsePacket.parse_obj(d)
        case None:
            return d
        case _:
            logger.error(f"Unknown class {d['_classname_']}")
            raise ValueError(f"Unknown class {d['_classname_']}")


db_engine = sqlmodel.create_engine(
    settings.database_uri,
    json_serializer=custom_json_serializer,
    json_deserializer=custom_json_deserializer,
)
