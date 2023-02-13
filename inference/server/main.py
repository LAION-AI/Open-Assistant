import asyncio
import contextlib
import time
from pathlib import Path

import alembic.command
import alembic.config
import fastapi
import redis.asyncio as redis
import sqlmodel
import websockets.exceptions
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_inference_server import interface, models, queueing
from oasst_inference_server.chat_repository import ChatRepository
from oasst_inference_server.database import db_engine
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference
from prometheus_fastapi_instrumentator import Instrumentator
from sse_starlette.sse import EventSourceResponse

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


# create async redis client
redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True
)


def create_session():
    with sqlmodel.Session(db_engine) as session:
        yield session


@contextlib.contextmanager
def manual_create_session():
    with contextlib.contextmanager(create_session)() as session:
        yield session


def create_chat_repository(session: sqlmodel.Session = Depends(create_session)):
    repository = ChatRepository(session)
    return repository


@contextlib.contextmanager
def manual_chat_repository():
    with manual_create_session() as session:
        yield create_chat_repository(session)


api_key_header = fastapi.Header(None, alias="X-API-Key")


def get_api_key(api_key: str = api_key_header) -> str:
    if api_key is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    return api_key


protocol_version_header = fastapi.Header(None, alias="X-Protocol-Version")


def get_protocol_version(protocol_version: str = protocol_version_header) -> str:
    if protocol_version != inference.INFERENCE_PROTOCOL_VERSION:
        logger.warning(f"Got worker with incompatible protocol version: {protocol_version}")
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_426_UPGRADE_REQUIRED,
            detail=f"Incompatible protocol version: {protocol_version}. Expected: {inference.INFERENCE_PROTOCOL_VERSION}.",
        )
    return protocol_version


def get_worker(
    api_key: str = Depends(get_api_key),
    protocol_version: str = Depends(get_protocol_version),
    session: sqlmodel.Session = Depends(create_session),
) -> models.DbWorkerEntry:
    logger.info(f"get_worker: {api_key=}, {protocol_version=}")
    worker = session.exec(
        sqlmodel.select(models.DbWorkerEntry).where(models.DbWorkerEntry.api_key == api_key)
    ).one_or_none()
    if worker is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return worker


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
    logger.info("Adding debug API keys")
    with manual_create_session() as session:
        for api_key in settings.debug_api_keys:
            logger.info(f"Checking if debug API key {api_key} exists")
            if (
                session.exec(
                    sqlmodel.select(models.DbWorkerEntry).where(models.DbWorkerEntry.api_key == api_key)
                ).one_or_none()
                is None
            ):
                logger.info(f"Adding debug API key {api_key}")
                session.add(models.DbWorkerEntry(api_key=api_key, name="Debug API Key"))
                session.commit()
            else:
                logger.info(f"Debug API key {api_key} already exists")


@app.get("/chat")
async def list_chats(chat_repository: ChatRepository = Depends(create_chat_repository)) -> interface.ListChatsResponse:
    """Lists all chats."""
    logger.info("Listing all chats.")
    chats = chat_repository.get_chat_list()
    return interface.ListChatsResponse(chats=chats)


@app.post("/chat")
async def create_chat(
    request: interface.CreateChatRequest, chat_repository: ChatRepository = Depends(create_chat_repository)
) -> interface.ChatListEntry:
    """Allows a client to create a new chat."""
    logger.info(f"Received {request=}")
    chat = chat_repository.create_chat()
    return chat.to_list_entry()


@app.get("/chat/{id}")
async def get_chat(id: str, chat_repository: ChatRepository = Depends(create_chat_repository)) -> interface.ChatEntry:
    """Allows a client to get the current state of a chat."""
    chat = chat_repository.get_chat_entry_by_id(id)
    return chat


@app.post("/chat/{chat_id}/message")
async def create_message(
    chat_id: str,
    message_request: interface.MessageRequest,
    fastapi_request: fastapi.Request,
    chat_repository: ChatRepository = Depends(create_chat_repository),
) -> EventSourceResponse:
    """Allows the client to stream the results of a request."""

    try:
        chat_repository.add_prompter_message(chat_id=chat_id, message_request=message_request)
        queue = queueing.work_queue(redis_client, message_request.worker_compat_hash)
        logger.debug(f"Adding {chat_id} to {queue.queue_id}")
        await queue.enqueue(chat_id)
        logger.debug(f"Added message to {queue.queue_id} for {chat_id}")
    except Exception:
        logger.exception("Error adding prompter message")
        return fastapi.Response(status_code=500)

    async def event_generator(chat_id):
        queue = queueing.chat_queue(redis_client, chat_id)
        result_data = []
        try:
            while True:
                if await fastapi_request.is_disconnected():
                    logger.warning("Client disconnected")
                    return
                item = await queue.dequeue()
                if item is None:
                    continue

                _, response_packet_str = item
                response_packet = inference.WorkResponsePacket.parse_raw(response_packet_str)
                result_data.append(response_packet)

                if response_packet.is_end:
                    break

                yield {
                    "retry": settings.sse_retry_timeout,
                    "data": interface.TokenResponseEvent(token=response_packet.token).json(),
                }
            logger.info(f"Finished streaming {chat_id} {len(result_data)=}")
        except Exception:
            logger.exception(f"Error streaming {chat_id}")
            raise

        try:
            with manual_chat_repository() as chat_repository:
                chat_repository.add_assistant_message(chat_id=chat_id, text=response_packet.generated_text.text)
        except Exception:
            logger.exception("Error adding assistant message")

    return EventSourceResponse(event_generator(chat_id))


@app.websocket("/work")
async def work(websocket: fastapi.WebSocket, worker: models.DbWorkerEntry = Depends(get_worker)):
    await websocket.accept()
    worker_config = inference.WorkerConfig.parse_raw(await websocket.receive_text())
    work_queue = queueing.work_queue(redis_client, worker_config.compat_hash)
    try:
        while True:
            if websocket.client_state == fastapi.websockets.WebSocketState.DISCONNECTED:
                logger.warning("Worker disconnected")
                break
            # find a pending task that matches the worker's config
            # could also be implemented using task queues
            # but general compatibility matching is tricky
            item = await work_queue.dequeue()
            if item is None:
                await asyncio.sleep(1)
                continue
            else:
                _, chat_id = item

            with manual_chat_repository() as chat_repository:
                chat = chat_repository.get_chat_by_id(chat_id)
                request = chat.pending_message_request

                chat_repository.set_chat_state(chat.id, interface.MessageRequestState.in_progress)

                work_request = inference.WorkRequest(
                    conversation=chat.conversation,
                    model_name=request.model_name,
                    max_new_tokens=request.max_new_tokens,
                )

                logger.info(f"Created {work_request=}")
                try:
                    await websocket.send_text(work_request.json())
                except websockets.exceptions.ConnectionClosedError:
                    logger.warning("Worker disconnected")
                    websocket.close()
                    chat_repository.set_chat_state(chat.id, interface.MessageRequestState.pending)
                    await work_queue.enqueue(chat.id)
                    break

                logger.debug(f"Sent {work_request=} to worker.")

                chat_queue = queueing.chat_queue(redis_client, chat.id)

                try:
                    in_progress = False
                    while True:
                        # maybe unnecessary to parse and re-serialize
                        # could just pass the raw string and mark end via empty string
                        response_packet = inference.WorkResponsePacket.parse_raw(await websocket.receive_text())
                        in_progress = True
                        await chat_queue.enqueue(response_packet.json())
                        if response_packet.is_end:
                            logger.debug(f"Received {response_packet=} from worker. Ending.")
                            break
                except fastapi.WebSocketException:
                    # TODO: handle this better
                    logger.exception(f"Websocket closed during handling of {chat.id}")
                    if in_progress:
                        logger.warning(f"Aborting {chat.id=}")
                        chat_repository.set_chat_state(chat.id, interface.MessageRequestState.aborted_by_worker)
                    else:
                        logger.warning(f"Marking {chat.id=} as pending since no work was done.")
                        chat_repository.set_chat_state(chat.id, interface.MessageRequestState.pending)
                        await work_queue.enqueue(chat.id)
                    raise

                chat_repository.set_chat_state(chat.id, interface.MessageRequestState.complete)
    except fastapi.WebSocketException:
        logger.exception("Websocket closed")


@app.put("/worker")
def create_worker(
    request: interface.CreateWorkerRequest,
    root_token: str = fastapi.Depends(get_root_token),
    session: sqlmodel.Session = fastapi.Depends(create_session),
):
    """Allows a client to register a worker."""
    worker = models.DbWorkerEntry(
        name=request.name,
    )
    session.add(worker)
    session.commit()
    session.refresh(worker)
    return worker


@app.get("/worker")
def list_workers(
    root_token: str = fastapi.Depends(get_root_token),
    session: sqlmodel.Session = fastapi.Depends(create_session),
):
    """Lists all workers."""
    workers = session.exec(sqlmodel.select(models.DbWorkerEntry)).all()
    return list(workers)


@app.delete("/worker/{worker_id}")
def delete_worker(
    worker_id: str,
    root_token: str = fastapi.Depends(get_root_token),
    session: sqlmodel.Session = fastapi.Depends(create_session),
):
    """Deletes a worker."""
    worker = session.get(models.DbWorkerEntry, worker_id)
    session.delete(worker)
    session.commit()
    return fastapi.Response(status_code=200)
