import redis.asyncio as redis
from oasst_inference_server.settings import settings


class QueueFullException(Exception):
    pass


class RedisQueue:
    def __init__(
        self,
        redis_client: redis.Redis,
        queue_id: str,
        expire: int | None = None,
        with_counter: bool = False,
        counter_pos_expire: int = 1,
        max_size: int | None = None,
    ) -> None:
        self.redis_client = redis_client
        self.queue_id = queue_id
        self.expire = expire
        self.with_counter = with_counter
        self.counter_pos_expire = counter_pos_expire
        self.max_size = max_size or 0

    async def enqueue(self, value: str, enforce_max_size: bool = True) -> int | None:
        if enforce_max_size and self.max_size > 0:
            if await self.get_length() >= self.max_size:
                raise QueueFullException()
        await self.redis_client.rpush(self.queue_id, value)
        if self.expire is not None:
            await self.set_expire(self.expire)
        if self.with_counter:
            ctr = await self.redis_client.incr(f"ctr_enq:{self.queue_id}")
            await self.redis_client.set(f"pos:{value}", ctr, ex=self.counter_pos_expire)
        else:
            ctr = None
        return ctr

    async def dequeue(self, timeout: int = 1) -> str | None:
        val = await self.redis_client.blpop(self.queue_id, timeout=timeout)
        if val is not None and self.with_counter:
            await self.redis_client.incr(f"ctr_deq:{self.queue_id}")
        return val

    async def set_expire(self, timeout: int) -> None:
        return await self.redis_client.expire(self.queue_id, timeout)

    async def get_enq_counter(self) -> int:
        if not self.with_counter:
            return 0
        enq = await self.redis_client.get(f"ctr_enq:{self.queue_id}")
        enq = int(enq) if enq is not None else 0
        return enq

    async def get_deq_counter(self) -> int:
        if not self.with_counter:
            return 0
        deq = await self.redis_client.get(f"ctr_deq:{self.queue_id}")
        deq = int(deq) if deq is not None else 0
        return deq

    async def get_length(self) -> int:
        return await self.redis_client.llen(self.queue_id)


async def get_pos_value(redis_client: redis.Redis, message_id: str) -> int:
    val = await redis_client.get(f"pos:{message_id}")
    if val is None:
        return 0
    return int(val)


def message_queue(redis_client: redis.Redis, message_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"message:{message_id}", expire=settings.message_queue_expire)


def work_queue(redis_client: redis.Redis, worker_compat_hash: str) -> RedisQueue:
    if settings.allowed_worker_compat_hashes != "*":
        if worker_compat_hash not in settings.allowed_worker_compat_hashes_list:
            raise ValueError(f"Worker compat hash {worker_compat_hash} not allowed")
    return RedisQueue(
        redis_client,
        f"work:{worker_compat_hash}",
        with_counter=True,
        counter_pos_expire=settings.message_queue_expire,
        max_size=settings.work_queue_max_size,
    )


def compliance_queue(redis_client: redis.Redis, worker_id: str) -> RedisQueue:
    return RedisQueue(redis_client, f"compliance:{worker_id}")
