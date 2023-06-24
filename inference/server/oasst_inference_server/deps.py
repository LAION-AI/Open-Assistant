import contextlib

import fastapi
import redis.asyncio as redis
from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
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


async def user_identifier(request: fastapi.Request) -> str:
    """Identify a request by user based on auth header"""
    trusted_client_token = request.headers.get("TrustedClient")
    if trusted_client_token is not None:
        return auth.get_user_id_from_trusted_client_token(trusted_client_token)

    token = request.headers.get("Authorization")
    return auth.get_user_id_from_auth_token(token)


class UserRateLimiter(RateLimiter):
    def __init__(
        self, times: int = 100, milliseconds: int = 0, seconds: int = 0, minutes: int = 1, hours: int = 0
    ) -> None:
        super().__init__(times, milliseconds, seconds, minutes, hours, user_identifier)
