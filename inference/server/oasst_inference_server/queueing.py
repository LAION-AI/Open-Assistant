import redis.asyncio as redis
from oasst_inference_server.settings import settings


class RedisQueue:
    def __init__(self, redis_client: redis.Redis, queue_id: str) -> None:
        self.redis_client = redis_client
        self.queue_id = queue_id

    async def enqueue(self, value: str) -> None:
        return await self.redis_client.rpush(self.queue_id, value)

    async def dequeue(self, block: bool = True, timeout: int = 1) -> str:
        if block:
            return await self.redis_client.blpop(self.queue_id, timeout=timeout)
        else:
            return await self.redis_client.lpop(self.queue_id)


def chat_queue(redis_client: redis.Redis, chat_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"chat:{chat_id}")


def message_queue(redis_client: redis.Redis, message_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"message:{message_id}")


def work_queue(redis_client: redis.Redis, worker_compat_hash: str) -> RedisQueue:
    if worker_compat_hash not in settings.allowed_worker_compat_hashes:
        raise ValueError(f"Worker compat hash {worker_compat_hash} not allowed")
    return RedisQueue(redis_client, f"work:{worker_compat_hash}")


def compliance_queue(redis_client: redis.Redis, worker_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"compliance:{worker_id}")
