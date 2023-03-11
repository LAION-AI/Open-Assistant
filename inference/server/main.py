import asyncio
import signal
import sys

import fastapi
import sqlmodel
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_inference_server import database, deps, models
from oasst_inference_server.routes import admin, auth, chats, workers
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference
from prometheus_fastapi_instrumentator import Instrumentator

app = fastapi.FastAPI()


# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_exceptions(request: fastapi.Request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Exception in request")
        raise
    return response


# add prometheus metrics at /metrics
@app.on_event("startup")
async def enable_prom_metrics():
    Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def log_inference_protocol_version():
    logger.info(f"Inference protocol version: {inference.INFERENCE_PROTOCOL_VERSION}")


def terminate_server(signum, frame):
    logger.info(f"Signal {signum}. Terminating server...")
    sys.exit(0)


@app.on_event("startup")
async def alembic_upgrade():
    signal.signal(signal.SIGINT, terminate_server)
    if not settings.update_alembic:
        logger.info("Skipping alembic upgrade on startup (update_alembic is False)")
        return
    logger.info("Attempting to upgrade alembic on startup")
    retry = 0
    while True:
        try:
            async with database.make_engine().begin() as conn:
                await conn.run_sync(database.alembic_upgrade)
            logger.info("Successfully upgraded alembic on startup")
            break
        except Exception:
            logger.exception("Alembic upgrade failed on startup")
            retry += 1
            if retry >= settings.alembic_retries:
                raise

            timeout = settings.alembic_retry_timeout * 2**retry
            logger.warning(f"Retrying alembic upgrade in {timeout} seconds")
            await asyncio.sleep(timeout)
    signal.signal(signal.SIGINT, signal.SIG_DFL)


@app.on_event("startup")
async def maybe_add_debug_api_keys():
    if not settings.debug_api_keys:
        logger.info("No debug API keys configured, skipping")
        return
    try:
        logger.info("Adding debug API keys")
        async with deps.manual_create_session() as session:
            for api_key in settings.debug_api_keys:
                logger.info(f"Checking if debug API key {api_key} exists")
                if (
                    await session.exec(sqlmodel.select(models.DbWorker).where(models.DbWorker.api_key == api_key))
                ).one_or_none() is None:
                    logger.info(f"Adding debug API key {api_key}")
                    session.add(models.DbWorker(api_key=api_key, name="Debug API Key"))
                    await session.commit()
                else:
                    logger.info(f"Debug API key {api_key} already exists")
    except Exception:
        logger.exception("Failed to add debug API keys")
        raise


# add routes
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(chats.router)
app.include_router(workers.router)
