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
from oasst_inference_server import interface
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


# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# create async redis client
redisClient = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True
)


def create_session():
    with sqlmodel.Session(db_engine) as session:
        yield session


def create_chat_repository(session: sqlmodel.Session = Depends(create_session)):
    repository = ChatRepository(session)
    return repository


if settings.update_alembic:

    @app.on_event("startup")
    def alembic_upgrade():
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
    logger.info(f"Received {request}")
    chat = chat_repository.create_chat()
    return chat.to_list_entry()


@app.get("/chat/{id}")
async def get_chat(id: str, chat_repository: ChatRepository = Depends(create_chat_repository)) -> interface.ChatEntry:
    """Allows a client to get the current state of a chat."""
    chat = chat_repository.get_chat_entry_by_id(id)
    return chat


@app.post("/chat/{id}/message")
async def create_message(
    id: str,
    message_request: interface.MessageRequest,
    fastapi_request: fastapi.Request,
    chat_repository: ChatRepository = Depends(create_chat_repository),
) -> EventSourceResponse:
    """Allows the client to stream the results of a request."""

    try:
        chat_repository.add_prompter_message(id=id, message_request=message_request)
    except Exception:
        logger.exception("Error adding prompter message")
        return fastapi.Response(status_code=500)

    async def event_generator(id):
        result_data = []

        try:
            while True:
                if await fastapi_request.is_disconnected():
                    logger.warning("Client disconnected")
                    return

                item = await redisClient.blpop(id, 1)
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
            logger.info(f"Finished streaming {id} {len(result_data)=}")
        except Exception:
            logger.exception(f"Error streaming {id}")
            raise

        try:
            with contextlib.contextmanager(create_session)() as session:
                chat_repository = create_chat_repository(session)
                chat_repository.add_assistant_message(id=id, text=response_packet.generated_text.text)
        except Exception:
            logger.exception("Error adding assistant message")

    return EventSourceResponse(event_generator(id))


@app.websocket("/work")
async def work(websocket: fastapi.WebSocket, chat_repository: ChatRepository = Depends(create_chat_repository)):
    await websocket.accept()
    worker_config = inference.WorkerConfig.parse_raw(await websocket.receive_text())
    try:
        while True:
            if websocket.client_state == fastapi.websockets.WebSocketState.DISCONNECTED:
                logger.warning("Worker disconnected")
                break
            # find a pending task that matches the worker's config
            # could also be implemented using task queues
            # but general compatibility matching is tricky
            for chat in chat_repository.get_pending_chats():
                request = chat.pending_message_request
                if request.compatible_with(worker_config):
                    break
            else:
                await asyncio.sleep(1)
                continue

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
                break

            logger.debug(f"Sent {work_request=} to worker.")

            try:
                in_progress = False
                while True:
                    # maybe unnecessary to parse and re-serialize
                    # could just pass the raw string and mark end via empty string
                    response_packet = inference.WorkResponsePacket.parse_raw(await websocket.receive_text())
                    in_progress = True
                    await redisClient.rpush(chat.id, response_packet.json())
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
                raise

            chat_repository.set_chat_state(chat.id, interface.MessageRequestState.complete)
    except fastapi.WebSocketException:
        logger.exception("Websocket closed")
