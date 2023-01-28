import asyncio
import enum
import uuid

import fastapi
import pydantic
import redis.asyncio as redis
import websockets.exceptions
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_shared.schemas import inference, protocol
from sse_starlette.sse import EventSourceResponse

app = fastapi.FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(pydantic.BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    sse_retry_timeout: int = 15000


settings = Settings()

# create async redis client
redisClient = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True
)


class CreateChatRequest(pydantic.BaseModel):
    pass


class CreateChatResponse(pydantic.BaseModel):
    id: str


class MessageRequest(pydantic.BaseModel):
    message: str = pydantic.Field(..., repr=False)
    model_name: str = "distilgpt2"
    max_new_tokens: int = 100

    def compatible_with(self, worker_config: inference.WorkerConfig) -> bool:
        return self.model_name == worker_config.model_name


class TokenResponseEvent(pydantic.BaseModel):
    token: str


class MessageRequestState(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    aborted_by_worker = "aborted_by_worker"


class DbChatEntry(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    conversation: protocol.Conversation = pydantic.Field(default_factory=protocol.Conversation)
    pending_message_request: MessageRequest | None = None
    message_request_state: MessageRequestState | None = None


# TODO: make real database
CHATS: dict[str, DbChatEntry] = {}


@app.post("/chat")
async def create_chat(request: CreateChatRequest) -> CreateChatResponse:
    """Allows a client to create a new chat."""
    logger.info(f"Received {request}")
    chat = DbChatEntry()
    CHATS[chat.id] = chat
    return CreateChatResponse(id=chat.id)


@app.get("/chat/{id}")
async def get_chat(id: str) -> protocol.Conversation:
    """Allows a client to get the current state of a chat."""
    return CHATS[id].conversation


@app.post("/chat/{id}/message")
async def create_message(id: str, message_request: MessageRequest, fastapi_request: fastapi.Request):
    """Allows the client to stream the results of a request."""

    chat = CHATS[id]
    if not chat.conversation.is_prompter_turn:
        raise fastapi.HTTPException(status_code=400, detail="Not your turn")
    if chat.pending_message_request is not None:
        raise fastapi.HTTPException(status_code=400, detail="Already pending")

    chat.conversation.messages.append(
        protocol.ConversationMessage(
            text=message_request.message,
            is_assistant=False,
        )
    )

    chat.pending_message_request = message_request
    chat.message_request_state = MessageRequestState.pending

    async def event_generator():
        result_data = []

        try:
            while True:
                if await fastapi_request.is_disconnected():
                    logger.warning("Client disconnected")
                    break

                item = await redisClient.blpop(chat.id, 1)
                if item is None:
                    continue

                _, response_packet_str = item
                response_packet = inference.WorkResponsePacket.parse_raw(response_packet_str)
                result_data.append(response_packet)

                if response_packet.is_end:
                    break

                yield {
                    "retry": settings.sse_retry_timeout,
                    "data": TokenResponseEvent(token=response_packet.token).json(),
                }
            logger.info(f"Finished streaming {chat.id} {len(result_data)=}")
        except Exception:
            logger.exception(f"Error streaming {chat.id}")

        chat.conversation.messages.append(
            protocol.ConversationMessage(
                text="".join([d.token for d in result_data[:-1]]),
                is_assistant=True,
            )
        )
        chat.pending_message_request = None

    return EventSourceResponse(event_generator())


@app.websocket("/work")
async def work(websocket: fastapi.WebSocket):
    await websocket.accept()
    worker_config = inference.WorkerConfig.parse_raw(await websocket.receive_text())
    try:
        while True:
            print(websocket.client_state)
            if websocket.client_state == fastapi.websockets.WebSocketState.DISCONNECTED:
                logger.warning("Worker disconnected")
                break
            # find a pending task that matches the worker's config
            # could also be implemented using task queues
            # but general compatibility matching is tricky
            for chat in CHATS.values():
                if (request := chat.pending_message_request) is not None:
                    if chat.message_request_state == MessageRequestState.pending:
                        if request.compatible_with(worker_config):
                            break
            else:
                logger.debug("No pending tasks")
                await asyncio.sleep(1)
                continue

            chat.message_request_state = MessageRequestState.in_progress

            work_request = inference.WorkRequest(
                conversation=chat.conversation,
                model_name=request.model_name,
                max_new_tokens=request.max_new_tokens,
            )

            logger.info(f"Created {work_request}")
            try:
                await websocket.send_text(work_request.json())
            except websockets.exceptions.ConnectionClosedError:
                logger.warning("Worker disconnected")
                websocket.close()
                chat.message_request_state = MessageRequestState.pending
                break

            try:
                while True:
                    # maybe unnecessary to parse and re-serialize
                    # could just pass the raw string and mark end via empty string
                    response_packet = inference.WorkResponsePacket.parse_raw(await websocket.receive_text())
                    await redisClient.rpush(chat.id, response_packet.json())
                    if response_packet.is_end:
                        break
            except fastapi.WebSocketException:
                # TODO: handle this better
                logger.exception(f"Websocket closed during handling of {chat.id}")
                chat.message_request_state = MessageRequestState.aborted_by_worker
                raise

            chat.message_request_state = MessageRequestState.complete
    except fastapi.WebSocketException:
        logger.exception("Websocket closed")
