# -*- coding: utf-8 -*-
from http import HTTPStatus
from pathlib import Path
from typing import Optional

import alembic.command
import alembic.config
import fastapi
import pydantic
from loguru import logger
from oasst_backend.api.deps import get_dummy_api_client
from oasst_backend.api.v1.api import api_router
from oasst_backend.config import settings
from oasst_backend.database import engine
from oasst_backend.exceptions import OasstError, OasstErrorCode
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware

app = fastapi.FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")


@app.exception_handler(OasstError)
async def oasst_exception_handler(request: fastapi.Request, ex: OasstError):
    logger.error(f"{request.method} {request.url} failed: {repr(ex)}")
    return fastapi.responses.JSONResponse(
        status_code=int(ex.http_status_code), content={"message": ex.message, "error_code": ex.error_code}
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


if settings.DEBUG_USE_SEED_DATA:

    @app.on_event("startup")
    def seed_data():
        class DummyPost(pydantic.BaseModel):
            task_post_id: str
            user_post_id: str
            parent_post_id: Optional[str]
            text: str
            role: str

        try:
            logger.info("Seed data check began")
            with Session(engine) as db:
                api_client = get_dummy_api_client(db)
                dummy_user = protocol_schema.User(id="__dummy_user__", display_name="Dummy User", auth_method="local")
                pr = PromptRepository(db=db, api_client=api_client, user=dummy_user)

                dummy_posts = [
                    DummyPost(
                        task_post_id="de111fa8",
                        user_post_id="6f1d0711",
                        parent_post_id=None,
                        text="Hi!",
                        role="user",
                    ),
                    DummyPost(
                        task_post_id="74c381d4",
                        user_post_id="4a24530b",
                        parent_post_id="6f1d0711",
                        text="Hello! How can I help you?",
                        role="assistant",
                    ),
                    DummyPost(
                        task_post_id="3d5dc440",
                        user_post_id="a8c01c04",
                        parent_post_id="4a24530b",
                        text="Do you have a recipe for potato soup?",
                        role="user",
                    ),
                    DummyPost(
                        task_post_id="643716c1",
                        user_post_id="f43a93b7",
                        parent_post_id="4a24530b",
                        text="Who were the 8 presidents before George Washington?",
                        role="user",
                    ),
                    DummyPost(
                        task_post_id="2e4e1e6",
                        user_post_id="c886920",
                        parent_post_id="6f1d0711",
                        text="Hey buddy! How can I serve you?",
                        role="assistant",
                    ),
                    DummyPost(
                        task_post_id="970c437d",
                        user_post_id="cec432cf",
                        parent_post_id=None,
                        text="euirdteunvglfe23908230892309832098 AAAAAAAA",
                        role="user",
                    ),
                    DummyPost(
                        task_post_id="6066118e",
                        user_post_id="4f85f637",
                        parent_post_id="cec432cf",
                        text="Sorry, I did not understand your request and it is unclear to me what you want me to do. Could you describe it in a different way?",
                        role="assistant",
                    ),
                    DummyPost(
                        task_post_id="ba87780d",
                        user_post_id="0e276b98",
                        parent_post_id="cec432cf",
                        text="I'm unsure how to interpret this. Is it a riddle?",
                        role="assistant",
                    ),
                ]

                for p in dummy_posts:
                    wp = pr.fetch_workpackage_by_postid(p.task_post_id)
                    if wp and not wp.ack:
                        logger.warning("Deleting unacknowledged seed data work package")
                        db.delete(wp)
                        wp = None
                    if not wp:
                        if p.parent_post_id is None:
                            wp = pr.store_task(
                                protocol_schema.InitialPromptTask(hint=""), thread_id=None, parent_post_id=None
                            )
                        else:
                            print("p.parent_post_id", p.parent_post_id)
                            parent_post = pr.fetch_post_by_frontend_post_id(p.parent_post_id, fail_if_missing=True)
                            wp = pr.store_task(
                                protocol_schema.AssistantReplyTask(
                                    conversation=protocol_schema.Conversation(
                                        messages=[protocol_schema.ConversationMessage(text="dummy", is_assistant=False)]
                                    )
                                ),
                                thread_id=parent_post.thread_id,
                                parent_post_id=parent_post.id,
                            )
                        pr.bind_frontend_post_id(wp.id, p.task_post_id)
                        post = pr.store_text_reply(p.text, p.task_post_id, p.user_post_id)

                        logger.info(
                            f"Inserted: post_id: {post.id}, payload: {post.payload.payload}, parent_post_id: {post.parent_id}"
                        )
                    else:
                        logger.debug(f"seed data work_package found: {wp.id}")
                logger.info("Seed data check completed")

        except Exception:
            logger.exception("Seed data insertion failed")


app.include_router(api_router, prefix=settings.API_V1_STR)
