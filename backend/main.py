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
from fastapi_utils.tasks import repeat_every
from loguru import logger
from oasst_backend.api.deps import api_auth, create_api_client
from oasst_backend.api.v1.api import api_router
from oasst_backend.api.v1.utils import prepare_conversation
from oasst_backend.config import settings
from oasst_backend.database import engine
from oasst_backend.models import message_tree_state
from oasst_backend.prompt_repository import PromptRepository, TaskRepository, UserRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.user_stats_repository import UserStatsRepository, UserStatsTimeFrame
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
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


if settings.OFFICIAL_WEB_API_KEY:

    @app.on_event("startup")
    def create_official_web_api_client():
        with Session(engine) as session:
            try:
                api_auth(settings.OFFICIAL_WEB_API_KEY, db=session)
            except OasstError:
                logger.info("Creating official web API client")
                create_api_client(
                    session=session,
                    api_key=settings.OFFICIAL_WEB_API_KEY,
                    description="The official web client for the OASST backend.",
                    frontend_type="web",
                    trusted=True,
                )


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
    @managed_tx_function(auto_commit=CommitMode.COMMIT)
    def create_seed_data(session: Session):
        class DummyMessage(BaseModel):
            task_message_id: str
            user_message_id: str
            parent_message_id: Optional[str]
            text: str
            lang: Optional[str]
            role: str
            tree_state: Optional[message_tree_state.State]

        if not settings.OFFICIAL_WEB_API_KEY:
            raise ValueError("Cannot use seed data without OFFICIAL_WEB_API_KEY")

        try:
            logger.info("Seed data check began")

            api_client = api_auth(settings.OFFICIAL_WEB_API_KEY, db=session)
            dummy_user = protocol_schema.User(id="__dummy_user__", display_name="Dummy User", auth_method="local")

            ur = UserRepository(db=session, api_client=api_client)
            tr = TaskRepository(db=session, api_client=api_client, client_user=dummy_user, user_repository=ur)
            pr = PromptRepository(
                db=session, api_client=api_client, client_user=dummy_user, user_repository=ur, task_repository=tr
            )
            tm = TreeManager(session, pr)

            with open(settings.DEBUG_USE_SEED_DATA_PATH) as f:
                dummy_messages_raw = json.load(f)

            dummy_messages = [DummyMessage(**dm) for dm in dummy_messages_raw]

            for msg in dummy_messages:
                task = tr.fetch_task_by_frontend_message_id(msg.task_message_id)
                if task and not task.ack:
                    logger.warning("Deleting unacknowledged seed data task")
                    session.delete(task)
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
                        conversation = prepare_conversation(conversation_messages)
                        if msg.role == "assistant":
                            task = tr.store_task(
                                protocol_schema.AssistantReplyTask(conversation=conversation),
                                message_tree_id=parent_message.message_tree_id,
                                parent_message_id=parent_message.id,
                            )
                        else:
                            task = tr.store_task(
                                protocol_schema.PrompterReplyTask(conversation=conversation),
                                message_tree_id=parent_message.message_tree_id,
                                parent_message_id=parent_message.id,
                            )
                    tr.bind_frontend_message_id(task.id, msg.task_message_id)
                    message = pr.store_text_reply(
                        msg.text,
                        msg.lang,
                        msg.task_message_id,
                        msg.user_message_id,
                        review_count=5,
                        review_result=True,
                        check_tree_state=False,
                    )
                    if message.parent_id is None:
                        tm._insert_default_state(
                            root_message_id=message.id, state=msg.tree_state or message_tree_state.State.GROWING
                        )
                        session.flush()

                    logger.info(
                        f"Inserted: message_id: {message.id}, payload: {message.payload.payload}, parent_message_id: {message.parent_id}"
                    )
                else:
                    logger.debug(f"seed data task found: {task.id}")

            logger.info("Seed data check completed")

        except Exception:
            logger.exception("Seed data insertion failed")


@app.on_event("startup")
def ensure_tree_states():
    try:
        logger.info("Startup: TreeManager.ensure_tree_states()")
        with Session(engine) as db:
            tm = TreeManager(db, None)
            tm.ensure_tree_states()

    except Exception:
        logger.exception("TreeManager.ensure_tree_states() failed.")


@app.on_event("startup")
@repeat_every(seconds=60 * settings.USER_STATS_INTERVAL_DAY, wait_first=False)
@managed_tx_function(auto_commit=CommitMode.COMMIT)
def update_leader_board_day(session: Session) -> None:
    try:
        usr = UserStatsRepository(session)
        usr.update_stats(time_frame=UserStatsTimeFrame.day)
    except Exception:
        logger.exception("Error during leaderboard update (daily)")


@app.on_event("startup")
@repeat_every(seconds=60 * settings.USER_STATS_INTERVAL_WEEK, wait_first=False)
@managed_tx_function(auto_commit=CommitMode.COMMIT)
def update_leader_board_week(session: Session) -> None:
    try:
        usr = UserStatsRepository(session)
        usr.update_stats(time_frame=UserStatsTimeFrame.week)
    except Exception:
        logger.exception("Error during user states update (weekly)")


@app.on_event("startup")
@repeat_every(seconds=60 * settings.USER_STATS_INTERVAL_MONTH, wait_first=False)
@managed_tx_function(auto_commit=CommitMode.COMMIT)
def update_leader_board_month(session: Session) -> None:
    try:
        usr = UserStatsRepository(session)
        usr.update_stats(time_frame=UserStatsTimeFrame.month)
    except Exception:
        logger.exception("Error during user states update (monthly)")


@app.on_event("startup")
@repeat_every(seconds=60 * settings.USER_STATS_INTERVAL_TOTAL, wait_first=False)
@managed_tx_function(auto_commit=CommitMode.COMMIT)
def update_leader_board_total(session: Session) -> None:
    try:
        usr = UserStatsRepository(session)
        usr.update_stats(time_frame=UserStatsTimeFrame.total)
    except Exception:
        logger.exception("Error during user states update (total)")


app.include_router(api_router, prefix=settings.API_V1_STR)


def get_openapi_schema():
    return json.dumps(app.openapi())


def export_ready_trees(file: Optional[str] = None, use_compression: bool = False):
    try:
        with Session(engine) as db:
            api_client = api_auth(settings.OFFICIAL_WEB_API_KEY, db=db)
            dummy_user = protocol_schema.User(id="__dummy_user__", display_name="Dummy User", auth_method="local")

            ur = UserRepository(db=db, api_client=api_client)
            tr = TaskRepository(db=db, api_client=api_client, client_user=dummy_user, user_repository=ur)
            pr = PromptRepository(
                db=db, api_client=api_client, client_user=dummy_user, user_repository=ur, task_repository=tr
            )
            tm = TreeManager(db, pr)

            tm.export_all_ready_trees(file, use_compression=use_compression)
    except Exception:
        logger.exception("Error exporting trees.")


def main():
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
    parser.add_argument(
        "--export", help="Export all trees which are ready for exporting.", action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "--export-file",
        help="Name of file to export trees to. If not provided when exporting, output will be send to STDOUT",
    )

    args = parser.parse_args()

    if args.print_openapi_schema:
        print(get_openapi_schema())
    elif args.export:
        use_compression: bool = ".gz" in args.export_file
        export_ready_trees(file=args.export_file, use_compression=use_compression)
    else:
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
