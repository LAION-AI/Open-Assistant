import json
import uuid

import pydantic
import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

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


@app.get("/stream/{queue_id}")
async def message_stream(queue_id: str, request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                logger.warning("Client disconnected")
                break
            item = await redisClient.blpop(queue_id, 1)
            if item is None:
                continue
            _, token = item

            if token == "<END>":
                await redisClient.delete(queue_id)
                break

            yield {
                "retry": settings.sse_retry_timeout,
                "data": json.dumps({"token": token}),
            }

    return EventSourceResponse(event_generator())


class CompleteRequest(pydantic.BaseModel):
    text: str
    model_name: str = "distilgpt2"


@app.post("/complete")
async def complete(request: CompleteRequest) -> str:
    queue_id = str(uuid.uuid4())
    work_queue_name = f"work-{request.model_name}"
    logger.info(f"Pushing {queue_id} {len(request.text)=} to {work_queue_name}")
    await redisClient.lpush(work_queue_name, json.dumps({"queue_id": queue_id, "text": request.text}))
    return queue_id
