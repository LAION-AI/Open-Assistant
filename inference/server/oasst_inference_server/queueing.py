import redis.asyncio as redis
from oasst_inference_server.settings import settings


class RedisQueue:
    def __init__(self, redis_client: redis.Redis, queue_id: str) -> None:
        self.redis_client = redis_client
        self.queue_id = queue_id

    async def enqueue(self, value: str, expire: int | None = None) -> None:
        pushed = await self.redis_client.rpush(self.queue_id, value)
        if expire is not None:
            await self.set_expire(expire)
        return pushed

    async def dequeue(self, timeout: int = 1) -> str:
        return await self.redis_client.blpop(self.queue_id, timeout=timeout)

    async def set_expire(self, timeout: int) -> None:
        return await self.redis_client.expire(self.queue_id, timeout)


def chat_queue(redis_client: redis.Redis, chat_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"chat:{chat_id}")


def message_queue(redis_client: redis.Redis, message_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"message:{message_id}")


def work_queue(redis_client: redis.Redis, worker_compat_hash: str) -> RedisQueue:
    if settings.allowed_worker_compat_hashes != "*":
        if worker_compat_hash not in settings.allowed_worker_compat_hashes_list:
            raise ValueError(f"Worker compat hash {worker_compat_hash} not allowed")
    return RedisQueue(redis_client, f"work:{worker_compat_hash}")


def compliance_queue(redis_client: redis.Redis, worker_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"compliance:{worker_id}")
