import asyncio
import enum
import random
import uuid

import fastapi
import pydantic
import redis.asyncio as redis
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from oasst_shared.schemas import inference
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


class CompletionRequest(pydantic.BaseModel):
    prompt: str = pydantic.Field(..., repr=False)
    model_name: str = "distilgpt2"
    max_length: int = 100

    def compatible_with(self, worker_config: inference.WorkerConfig) -> bool:
        return self.model_name == worker_config.model_name


class CompletionResponse(pydantic.BaseModel):
    id: str


class ResponseEvent(pydantic.BaseModel):
    token: str


class CompletionState(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"


class DbEntry(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    completion_request: CompletionRequest
    seed: int = pydantic.Field(default_factory=lambda: random.randint(0, 2**32 - 1))
    result_data: list[inference.WorkResponsePacket] | None = None
    state: CompletionState = CompletionState.pending


# TODO: make real database
DATABASE: dict[str, DbEntry] = {}


@app.post("/complete")
async def complete(request: CompletionRequest) -> CompletionResponse:
    """Allows a client to request completion of a prompt."""
    logger.info(f"Received {request}")

    db_entry = DbEntry(
        completion_request=request,
    )
    DATABASE[db_entry.id] = db_entry
    return CompletionResponse(id=db_entry.id)


@app.websocket("/work")
async def work(websocket: fastapi.WebSocket):
    await websocket.accept()
    worker_config = inference.WorkerConfig.parse_raw(await websocket.receive_text())
    while True:
        # find a pending task that matches the worker's config
        # could also be implemented using task queues
        # but general compatibility matching is tricky
        for db_entry in DATABASE.values():
            if db_entry.state == CompletionState.pending:
                if db_entry.completion_request.compatible_with(worker_config):
                    break
        else:
            logger.debug("No pending tasks")
            await asyncio.sleep(1)
            continue

        request = db_entry.completion_request

        work_request = inference.WorkRequest(
            prompt=request.prompt,
            model_name=request.model_name,
            max_length=request.max_length,
            seed=db_entry.seed,
        )

        logger.info(f"Created {work_request}")
        db_entry.state = CompletionState.in_progress
        try:
            await websocket.send_text(work_request.json())
            while True:
                # maybe unnecessary to parse and re-serialize
                # could just pass the raw string and mark end via empty string
                response_packet = inference.WorkResponsePacket.parse_raw(await websocket.receive_text())
                await redisClient.rpush(db_entry.id, response_packet.json())
                if response_packet.is_end:
                    break
        except fastapi.WebSocketException:
            # TODO: handle this better
            logger.exception(f"Websocket closed during handling of {db_entry.id}")


@app.get("/stream/{id}")
async def message_stream(id: str, request: fastapi.Request):
    """Allows the client to stream the results of a request."""

    db_entry = DATABASE[id]

    if db_entry.state not in (CompletionState.pending, CompletionState.in_progress):
        raise fastapi.HTTPException(status_code=404, detail="Request not found")

    async def event_generator():
        result_data = []

        try:
            while True:
                if await request.is_disconnected():
                    logger.warning("Client disconnected")
                    break

                item = await redisClient.blpop(db_entry.id, 1)
                if item is None:
                    continue

                _, response_packet_str = item
                response_packet = inference.WorkResponsePacket.parse_raw(response_packet_str)
                result_data.append(response_packet)

                if response_packet.is_end:
                    break

                yield {
                    "retry": settings.sse_retry_timeout,
                    "data": ResponseEvent(token=response_packet.token).json(),
                }
            logger.info(f"Finished streaming {db_entry.id} {len(result_data)=}")
        except Exception:
            logger.exception(f"Error streaming {db_entry.id}")

        # store the generated data in the database
        db_entry.result_data = result_data
        db_entry.state = CompletionState.complete

    return EventSourceResponse(event_generator())
