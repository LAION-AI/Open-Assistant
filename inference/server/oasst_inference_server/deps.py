import contextlib

import fastapi
import redis.asyncio as redis
import sqlmodel
from fastapi import Depends, HTTPException
from oasst_inference_server import auth
from oasst_inference_server.chat_repository import ChatRepository
from oasst_inference_server.database import db_engine
from oasst_inference_server.settings import settings
from oasst_inference_server.user_chat_repository import UserChatRepository

# create async redis client
redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True
)


def create_session():
    with sqlmodel.Session(db_engine) as session:
        yield session


@contextlib.contextmanager
def manual_create_session():
    with contextlib.contextmanager(create_session)() as session:
        yield session


def create_chat_repository(session: sqlmodel.Session = Depends(create_session)) -> ChatRepository:
    repository = ChatRepository(session)
    return repository


def create_user_chat_repository(
    session: sqlmodel.Session = Depends(create_session),
    user_id: str = Depends(auth.get_current_user_id),
) -> UserChatRepository:
    repository = UserChatRepository(session=session, user_id=user_id)
    return repository


@contextlib.contextmanager
def manual_chat_repository():
    with manual_create_session() as session:
        yield create_chat_repository(session)


@contextlib.contextmanager
def manual_user_chat_repository(user_id: str):
    with manual_create_session() as session:
        yield create_user_chat_repository(session, user_id)


def get_bearer_token(authorization_header: str) -> str:
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Authorization header must start with 'Bearer '")
    return authorization_header[len("Bearer ") :]


def get_root_token(token: str = Depends(get_bearer_token)) -> str:
    root_token = settings.root_token
    if token == root_token:
        return token
    raise HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )
