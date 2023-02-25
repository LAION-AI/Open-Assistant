import time
from pathlib import Path

import alembic.command
import alembic.config
import fastapi
import sqlmodel
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_inference_server import client_handler, deps, interface, models, worker_handler
from oasst_inference_server.chat_repository import ChatRepository
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference
from prometheus_fastapi_instrumentator import Instrumentator

app = fastapi.FastAPI()


# add prometheus metrics at /metrics
@app.on_event("startup")
async def enable_prom_metrics():
    Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def log_inference_protocol_version():
    logger.info(f"Inference protocol version: {inference.INFERENCE_PROTOCOL_VERSION}")


# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_bearer_token(authorization_header: str) -> str:
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Authorization header must start with 'Bearer '")
    return authorization_header[len("Bearer ") :]


def get_root_token(token: str = Depends(get_bearer_token)) -> str:
    root_token = settings.root_token
    if token == root_token:
        return token
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


@app.on_event("startup")
def alembic_upgrade():
    if not settings.update_alembic:
        logger.info("Skipping alembic upgrade on startup (update_alembic is False)")
        return
    logger.info("Attempting to upgrade alembic on startup")
    retry = 0
    while True:
        try:
            alembic_ini_path = Path(__file__).parent / "alembic.ini"
            alembic_cfg = alembic.config.Config(str(alembic_ini_path))
            alembic_cfg.set_main_option("sqlalchemy.url", settings.database_uri)
            alembic.command.upgrade(alembic_cfg, "head")
            logger.info("Successfully upgraded alembic on startup")
            break
        except Exception:
            logger.exception("Alembic upgrade failed on startup")
            retry += 1
            if retry >= settings.alembic_retries:
                raise

            timeout = settings.alembic_retry_timeout * 2**retry
            logger.warning(f"Retrying alembic upgrade in {timeout} seconds")
            time.sleep(timeout)


@app.on_event("startup")
def maybe_add_debug_api_keys():
    if not settings.debug_api_keys:
        logger.info("No debug API keys configured, skipping")
        return
    try:
        logger.info("Adding debug API keys")
        with deps.manual_create_session() as session:
            for api_key in settings.debug_api_keys:
                logger.info(f"Checking if debug API key {api_key} exists")
                if (
                    session.exec(
                        sqlmodel.select(models.DbWorker).where(models.DbWorker.api_key == api_key)
                    ).one_or_none()
                    is None
                ):
                    logger.info(f"Adding debug API key {api_key}")
                    session.add(models.DbWorker(api_key=api_key, name="Debug API Key"))
                    session.commit()
                else:
                    logger.info(f"Debug API key {api_key} already exists")
    except Exception:
        logger.exception("Failed to add debug API keys")
        raise


@app.get("/chat")
async def list_chats(cr: ChatRepository = Depends(deps.create_chat_repository)) -> interface.ListChatsResponse:
    """Lists all chats."""
    logger.info("Listing all chats.")
    chats = cr.get_chat_list()
    return interface.ListChatsResponse(chats=chats)


@app.post("/chat")
async def create_chat(
    request: interface.CreateChatRequest, cr: ChatRepository = Depends(deps.create_chat_repository)
) -> interface.ChatListRead:
    """Allows a client to create a new chat."""
    logger.info(f"Received {request=}")
    chat = cr.create_chat()
    return chat.to_list_read()


@app.get("/chat/{id}")
async def get_chat(id: str, cr: ChatRepository = Depends(deps.create_chat_repository)) -> interface.ChatRead:
    """Allows a client to get the current state of a chat."""
    chat = cr.get_chat_by_id(id)
    return chat.to_read()


app.post("/chat/{chat_id}/message")(client_handler.handle_create_message)

app.websocket("/work")(worker_handler.handle_worker)


@app.put("/worker")
def create_worker(
    request: interface.CreateWorkerRequest,
    root_token: str = fastapi.Depends(get_root_token),
    session: sqlmodel.Session = fastapi.Depends(deps.create_session),
):
    """Allows a client to register a worker."""
    worker = models.DbWorker(
        name=request.name,
    )
    session.add(worker)
    session.commit()
    session.refresh(worker)
    return worker


@app.get("/worker")
def list_workers(
    root_token: str = fastapi.Depends(get_root_token),
    session: sqlmodel.Session = fastapi.Depends(deps.create_session),
):
    """Lists all workers."""
    workers = session.exec(sqlmodel.select(models.DbWorker)).all()
    return list(workers)


@app.delete("/worker/{worker_id}")
def delete_worker(
    worker_id: str,
    root_token: str = fastapi.Depends(get_root_token),
    session: sqlmodel.Session = fastapi.Depends(deps.create_session),
):
    """Deletes a worker."""
    worker = session.get(models.DbWorker, worker_id)
    session.delete(worker)
    session.commit()
    return fastapi.Response(status_code=200)
