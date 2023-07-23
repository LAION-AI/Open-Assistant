import contextlib

import redis.asyncio as redis
from fastapi import Depends
from oasst_inference_server import auth
from oasst_inference_server.chat_repository import ChatRepository
from oasst_inference_server.database import AsyncSession, get_async_session
from oasst_inference_server.settings import settings
from oasst_inference_server.user_chat_repository import UserChatRepository


# create async redis client
def make_redis_client():
    redis_client = redis.Redis(
        host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True
    )
    return redis_client


redis_client = make_redis_client()


async def create_session():
    async for session in get_async_session():
        yield session


@contextlib.asynccontextmanager
async def manual_create_session(autoflush=True):
    async with contextlib.asynccontextmanager(get_async_session)(autoflush=autoflush) as session:
        yield session


async def create_chat_repository(session: AsyncSession = Depends(create_session)) -> ChatRepository:
    repository = ChatRepository(session=session)
    return repository


async def create_user_chat_repository(
    session: AsyncSession = Depends(create_session),
    user_id: str = Depends(auth.get_current_user_id),
) -> UserChatRepository:
    repository = UserChatRepository(session=session, user_id=user_id)
    return repository


@contextlib.asynccontextmanager
async def manual_chat_repository():
    async with manual_create_session() as session:
        yield await create_chat_repository(session)


@contextlib.asynccontextmanager
async def manual_user_chat_repository(user_id: str):
    async with manual_create_session() as session:
        yield await create_user_chat_repository(session, user_id)
