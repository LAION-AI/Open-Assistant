from http import HTTPStatus
from secrets import token_hex
from typing import Generator
from uuid import UUID

from fastapi import Depends, Request, Response, Security
from fastapi.security.api_key import APIKey, APIKeyHeader, APIKeyQuery
from fastapi_limiter.depends import RateLimiter
from loguru import logger
from oasst_backend.config import settings
from oasst_backend.database import engine
from oasst_backend.models import ApiClient
from oasst_shared.exceptions import OasstError, OasstErrorCode
from sqlmodel import Session


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


def get_dummy_api_client(db: Session) -> ApiClient:
    # make sure that a dummy api key exits in db (foreign key references)
    ANY_API_KEY_ID = UUID("00000000-1111-2222-3333-444444444444")
    api_client: ApiClient = db.query(ApiClient).filter(ApiClient.id == ANY_API_KEY_ID).first()
    if api_client is None:
        token = token_hex(32)
        logger.info(f"ANY_API_KEY missing, inserting api_key: {token}")
        api_client = ApiClient(
            id=ANY_API_KEY_ID,
            api_key=token,
            description="ANY_API_KEY, random token",
            trusted=True,
            frontend_type="Test frontend",
        )
        db.add(api_client)
        db.commit()
    return api_client


def api_auth(
    api_key: APIKey,
    db: Session,
) -> ApiClient:
    if api_key or settings.DEBUG_SKIP_API_KEY_CHECK:

        if settings.DEBUG_SKIP_API_KEY_CHECK or settings.DEBUG_ALLOW_ANY_API_KEY:
            return get_dummy_api_client(db)

        api_client = db.query(ApiClient).filter(ApiClient.api_key == api_key).first()
        if api_client is not None and api_client.enabled:
            return api_client

    raise OasstError(
        "Could not validate credentials",
        error_code=OasstErrorCode.API_CLIENT_NOT_AUTHORIZED,
        http_status_code=HTTPStatus.FORBIDDEN,
    )


def get_api_client(
    api_key: APIKey = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    return api_auth(api_key, db)


def get_trusted_api_client(
    api_key: APIKey = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    client = api_auth(api_key, db)
    if not client.trusted:
        raise OasstError(
            "Forbidden",
            error_code=OasstErrorCode.API_CLIENT_NOT_AUTHORIZED,
            http_status_code=HTTPStatus.FORBIDDEN,
        )
    return client


class UserRateLimiter(RateLimiter):
    def __init__(
        self, times: int = 100, milliseconds: int = 0, seconds: int = 0, minutes: int = 1, hours: int = 0
    ) -> None:
        async def identifier(request: Request) -> str:
            """Identify a request based on api_key and user.id"""
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            user = (await request.json()).get("user")
            return f"{api_key}:{user.get('id')}"

        super().__init__(times, milliseconds, seconds, minutes, hours, identifier)

    async def __call__(self, request: Request, response: Response, api_key: str = Depends(get_api_key)) -> None:
        # Skip if rate limiting is disabled
        if not settings.RATE_LIMIT:
            return

        # Attempt to retrieve api_key and user information
        user = (await request.json()).get("user")

        # Skip when api_key and user information are not available
        # (such that it will be handled by `APIClientRateLimiter`)
        if not api_key or not user or not user.get("id"):
            return

        return await super().__call__(request, response)


class APIClientRateLimiter(RateLimiter):
    def __init__(
        self, times: int = 10_000, milliseconds: int = 0, seconds: int = 0, minutes: int = 1, hours: int = 0
    ) -> None:
        async def identifier(request: Request) -> str:
            """Identify a request based on api_key and user.id"""
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            return f"{api_key}"

        super().__init__(times, milliseconds, seconds, minutes, hours, identifier)

    async def __call__(self, request: Request, response: Response, api_key: str = Depends(get_api_key)) -> None:
        # Skip if rate limiting is disabled
        if not settings.RATE_LIMIT:
            return

        # Attempt to retrieve api_key and user information
        user = (await request.json()).get("user")

        # Skip if user information is available
        # (such that it will be handled by `UserRateLimiter`)
        if not api_key or user:
            return

        return await super().__call__(request, response)
