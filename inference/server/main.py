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
    completion_id: str


class ResponseEvent(pydantic.BaseModel):
    token: str


class CompletionState(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"


class DbEntry(pydantic.BaseModel):
    completion_request: CompletionRequest
    completion_id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    stream_queue_id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
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
    DATABASE[db_entry.completion_id] = db_entry
    return CompletionResponse(completion_id=db_entry.completion_id)


class StartWorkRequest(pydantic.BaseModel):
    worker_config: inference.WorkerConfig


@app.post("/work")
async def work(start_work_request: StartWorkRequest) -> inference.WorkRequest:
    """Allows a worker to request work, given its configuration."""

    # find a pending request that is compatible with the worker config
    # this could be implemented using queues, databases, long polling, etc.
    # we might also think about replacing this endpoint with a message queue
    # but we need to know which worker is dequeueing a particular request
    # to do proper credit assignment and load balancing (+ security)
    for db_entry in DATABASE.values():
        if db_entry.state == CompletionState.pending:
            if db_entry.completion_request.compatible_with(start_work_request.worker_config):
                break
    else:
        raise fastapi.HTTPException(status_code=202, detail="No pending requests")

    request = db_entry.completion_request

    work_request = inference.WorkRequest(
        stream_queue_id=db_entry.stream_queue_id,
        prompt=request.prompt,
        model_name=request.model_name,
        max_length=request.max_length,
        seed=db_entry.seed,
    )

    logger.info(f"Created {work_request}")
    db_entry.state = CompletionState.in_progress
    return work_request


@app.get("/stream/{db_id}")
async def message_stream(db_id: str, request: fastapi.Request):
    """Allows the client to stream the results of a request."""

    db_entry = DATABASE[db_id]

    if db_entry.state not in (CompletionState.pending, CompletionState.in_progress):
        raise fastapi.HTTPException(status_code=404, detail="Request not found")

    stream_queue_id = db_entry.stream_queue_id

    async def event_generator():
        result_data = []

        try:
            while True:
                if await request.is_disconnected():
                    logger.warning("Client disconnected")
                    break

                item = await redisClient.blpop(stream_queue_id, 1)
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
            logger.info(f"Finished streaming {stream_queue_id} {len(result_data)=}")
        except Exception:
            logger.exception(f"Error streaming {stream_queue_id}")

        # store the generated data in the database
        db_entry.result_data = result_data
        db_entry.state = CompletionState.complete

    return EventSourceResponse(event_generator())
