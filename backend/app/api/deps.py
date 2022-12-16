# -*- coding: utf-8 -*-
from secrets import token_hex
from typing import Generator
from uuid import UUID

from app.config import settings
from app.database import engine
from app.models import ApiClient
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKey, APIKeyHeader, APIKeyQuery
from loguru import logger
from sqlmodel import Session
from starlette.status import HTTP_403_FORBIDDEN


def get_db() -> Generator:
    with Session(engine) as db:
        yield db


api_key_query = APIKeyQuery(name="api_key", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
):
    if api_key_query:
        return api_key_query
    else:
        return api_key_header


def api_auth(
    api_key: APIKey,
    db: Session,
) -> ApiClient:

    if api_key is not None:
        if settings.ALLOW_ANY_API_KEY:
            # make sure that a dummy api key exits in db (foreign key references)
            ANY_API_KEY_ID = UUID("00000000-1111-2222-3333-444444444444")
            api_client: ApiClient = db.query(ApiClient).filter(ApiClient.id == ANY_API_KEY_ID).first()
            if api_client is None:
                token = token_hex(32)
                logger.info(f"ANY_API_KEY missing, inserting api_key: {token}")
                api_client = ApiClient(id=ANY_API_KEY_ID, api_key=token, description="ANY_API_KEY, random token")
                db.add(api_client)
                db.commit()
            return api_client

        api_client = db.query(ApiClient).filter(ApiClient.api_key == api_key).first()
        if api_client is not None and api_client.enabled:
            return api_client

    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")
