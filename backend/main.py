import json
from http import HTTPStatus
from math import ceil
from pathlib import Path

import alembic.command
import alembic.config
import fastapi
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from filldb import FillDb
from loguru import logger
from oasst_backend.api.v1.api import api_router
from oasst_backend.config import settings
from oasst_backend.database import engine
from oasst_backend.tree_manager import TreeManager, TreeManagerConfiguration
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
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
        fill_db = FillDb(engine)
        fill_db.fill_api_client()
        fill_db.fill_users()
        fill_db.fill_messages()


@app.on_event("startup")
def ensure_tree_states():
    try:
        logger.info("Startup: TreeManager.ensure_tree_states()")
        cfg = TreeManagerConfiguration()  # TODO: decide where config is stored, e.g. load form json/yaml file
        with Session(engine) as db:
            tm = TreeManager(db, None, configuration=cfg)
            tm.ensure_tree_states()

    except Exception:
        logger.exception("TreeManager.ensure_tree_states() failed.")


app.include_router(api_router, prefix=settings.API_V1_STR)


def get_openapi_schema():
    return json.dumps(app.openapi())


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

    args = parser.parse_args()

    if args.print_openapi_schema:
        print(get_openapi_schema())
    else:
        uvicorn.run(app, host=args.host, port=int(args.port))


if __name__ == "__main__":
    main()
