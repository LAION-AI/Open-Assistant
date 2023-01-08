import json
from http import HTTPStatus
from math import ceil
from pathlib import Path
from typing import Optional

import alembic.command
import alembic.config
import fastapi
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from loguru import logger
from oasst_backend.api.deps import get_dummy_api_client
from oasst_backend.api.v1.api import api_router
from oasst_backend.config import settings
from oasst_backend.database import engine
from oasst_backend.prompt_repository import PromptRepository, TaskRepository, UserRepository
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from pydantic import BaseModel
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware

app = fastapi.FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")


@app.exception_handler(OasstError)
async def oasst_exception_handler(request: fastapi.Request, ex: OasstError):
    logger.error(f"{request.method} {request.url} failed: {repr(ex)}")

    return fastapi.responses.JSONResponse(
        status_code=int(ex.http_status_code),
        content=protocol_schema.OasstErrorResponse(
            message=ex.message,
            error_code=OasstErrorCode(ex.error_code),
        ).dict(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: fastapi.Request, ex: Exception):
    logger.exception(f"{request.method} {request.url} failed [UNHANDLED]: {repr(ex)}")
    status = HTTPStatus.INTERNAL_SERVER_ERROR
    return fastapi.responses.JSONResponse(
        status_code=status.value, content={"message": status.name, "error_code": OasstErrorCode.GENERIC_ERROR}
    )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.UPDATE_ALEMBIC:

    @app.on_event("startup")
    def alembic_upgrade():
        logger.info("Attempting to upgrade alembic on startup")
        try:
            alembic_ini_path = Path(__file__).parent / "alembic.ini"
            alembic_cfg = alembic.config.Config(str(alembic_ini_path))
            alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URI)
            alembic.command.upgrade(alembic_cfg, "head")
            logger.info("Successfully upgraded alembic on startup")
        except Exception:
            logger.exception("Alembic upgrade failed on startup")


if settings.RATE_LIMIT:

    @app.on_event("startup")
    async def connect_redis():
        async def http_callback(request: fastapi.Request, response: fastapi.Response, pexpire: int):
            """Error callback function when too many requests"""
            expire = ceil(pexpire / 1000)
            raise OasstError(
                f"Too Many Requests. Retry After {expire} seconds.",
                OasstErrorCode.TOO_MANY_REQUESTS,
                HTTPStatus.TOO_MANY_REQUESTS,
            )

        try:
            redis_client = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0", encoding="utf-8", decode_responses=True
            )
            logger.info(f"Connected to {redis_client=}")
            await FastAPILimiter.init(redis_client, http_callback=http_callback)
        except Exception:
            logger.exception("Failed to establish Redis connection")


if settings.DEBUG_USE_SEED_DATA:

    @app.on_event("startup")
    def seed_data():
        class DummyMessage(BaseModel):
            task_message_id: str
            user_message_id: str
            parent_message_id: Optional[str]
            text: str
            role: str

        try:
            logger.info("Seed data check began")
            with Session(engine) as db:
                api_client = get_dummy_api_client(db)
                dummy_user = protocol_schema.User(id="__dummy_user__", display_name="Dummy User", auth_method="local")

                ur = UserRepository(db=db, api_client=api_client)
                tr = TaskRepository(db=db, api_client=api_client, client_user=dummy_user, user_repository=ur)
                pr = PromptRepository(
                    db=db, api_client=api_client, client_user=dummy_user, user_repository=ur, task_repository=tr
                )

                with open(settings.DEBUG_USE_SEED_DATA_PATH) as f:
                    dummy_messages_raw = json.load(f)

                dummy_messages = [DummyMessage(**dm) for dm in dummy_messages_raw]

                for msg in dummy_messages:
                    task = tr.fetch_task_by_frontend_message_id(msg.task_message_id)
                    if task and not task.ack:
                        logger.warning("Deleting unacknowledged seed data task")
                        db.delete(task)
                        task = None
                    if not task:
                        if msg.parent_message_id is None:
                            task = tr.store_task(
                                protocol_schema.InitialPromptTask(hint=""), message_tree_id=None, parent_message_id=None
                            )
                        else:
                            parent_message = pr.fetch_message_by_frontend_message_id(
                                msg.parent_message_id, fail_if_missing=True
                            )
                            conversation_messages = pr.fetch_message_conversation(parent_message)
                            conversation = protocol_schema.Conversation(
                                messages=[
                                    protocol_schema.ConversationMessage(
                                        text=cmsg.text,
                                        is_assistant=cmsg.role == "assistant",
                                        message_id=cmsg.id,
                                        fronend_message_id=cmsg.frontend_message_id,
                                    )
                                    for cmsg in conversation_messages
                                ]
                            )
                            task = tr.store_task(
                                protocol_schema.AssistantReplyTask(conversation=conversation),
                                message_tree_id=parent_message.message_tree_id,
                                parent_message_id=parent_message.id,
                            )
                        tr.bind_frontend_message_id(task.id, msg.task_message_id)
                        message = pr.store_text_reply(msg.text, msg.task_message_id, msg.user_message_id)

                        logger.info(
                            f"Inserted: message_id: {message.id}, payload: {message.payload.payload}, parent_message_id: {message.parent_id}"
                        )
                    else:
                        logger.debug(f"seed data task found: {task.id}")
                logger.info("Seed data check completed")

        except Exception:
            logger.exception("Seed data insertion failed")


app.include_router(api_router, prefix=settings.API_V1_STR)


def get_openapi_schema():
    return json.dumps(app.openapi())


if __name__ == "__main__":
    # Importing here so we don't import packages unnecessarily if we're
    # importing main as a module.
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--print-openapi-schema",
        help="Dumps the openapi schema to stdout",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument("--host", help="The host to run the server", default="0.0.0.0")
    parser.add_argument("--port", help="The port to run the server", default=8080)

    args = parser.parse_args()

    if args.print_openapi_schema:
        print(get_openapi_schema())
    else:
        uvicorn.run(app, host=args.host, port=args.port)
