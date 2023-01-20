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


class DbEntry(pydantic.BaseModel):
    completion_id: str
    completion_request: CompletionRequest
    work_request: inference.WorkRequest | None = None
    result_data: list[inference.WorkResponsePacket] | None = None


# TODO: make real database
DATABASE: dict[str, DbEntry] = {}


@app.post("/complete")
async def complete(request: CompletionRequest) -> CompletionResponse:
    """Allows a client to request completion of a prompt."""
    logger.info(f"Received {request}")
    completion_id = str(uuid.uuid4())
    DATABASE[completion_id] = DbEntry(completion_id=completion_id, completion_request=request)
    return CompletionResponse(completion_id=completion_id)


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
        if db_entry.completion_request and not db_entry.work_request:
            if db_entry.completion_request.compatible_with(start_work_request.worker_config):
                break
    else:
        raise fastapi.HTTPException(status_code=202, detail="No pending requests")

    request = db_entry.completion_request

    # generate a stream id to use for this request
    stream_queue_id = str(uuid.uuid4())
    seed = random.randint(0, 2**32 - 1)
    work_request = inference.WorkRequest(
        stream_queue_id=stream_queue_id,
        model_name=request.model_name,
        prompt=request.prompt,
        max_length=request.max_length,
        seed=seed,
    )

    # store the work request in the database
    db_entry.work_request = work_request

    logger.info(f"Created {work_request}")
    return work_request


@app.get("/stream/{db_id}")
async def message_stream(db_id: str, request: fastapi.Request):
    """Allows the client to stream the results of a request."""

    db_entry = DATABASE[db_id]
    if not db_entry.work_request:
        raise fastapi.HTTPException(status_code=202, detail="Not ready")

    stream_queue_id = db_entry.work_request.stream_queue_id

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
                    await redisClient.delete(stream_queue_id)
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

    return EventSourceResponse(event_generator())
