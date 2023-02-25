from http import HTTPStatus
from secrets import token_hex
from typing import Generator, NamedTuple, Optional
from uuid import UUID

from fastapi import Depends, Request, Response, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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


api_key_query = APIKeyQuery(name="api_key", scheme_name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", scheme_name="api-key", auto_error=False)
oasst_user_query = APIKeyQuery(name="oasst_user", scheme_name="oasst-user", auto_error=False)
oasst_user_header = APIKeyHeader(name="x-oasst-user", scheme_name="oasst-user", auto_error=False)

bearer_token = HTTPBearer(auto_error=False)


def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
) -> str:
    if api_key_query:
        return api_key_query
    else:
        return api_key_header


class FrontendUserId(NamedTuple):
    auth_method: str
    username: str


def get_frontend_user_id(
    user_query: str = Security(oasst_user_query),
    user_header: str = Security(oasst_user_header),
) -> FrontendUserId:
    def split_user(v: str) -> tuple[str, str]:
        if type(v) is str:
            v = v.split(":", maxsplit=1)
            if len(v) == 2:
                return FrontendUserId(auth_method=v[0], username=v[1])
        return FrontendUserId(auth_method=None, username=None)

    if user_query:
        return split_user(user_query)
    else:
        return split_user(user_header)


def create_api_client(
    *,
    session: Session,
    description: str,
    frontend_type: str,
    trusted: bool | None = False,
    admin_email: str | None = None,
    api_key: str | None = None,
    force_id: Optional[UUID] = None,
) -> ApiClient:
    if api_key is None:
        api_key = token_hex(32)

    logger.info(f"Creating new api client with {api_key=}")
    api_client = ApiClient(
        api_key=api_key,
        description=description,
        frontend_type=frontend_type,
        trusted=trusted,
        admin_email=admin_email,
    )
    if force_id:
        api_client.id = force_id
    session.add(api_client)
    session.commit()
    session.refresh(api_client)
    return api_client


def api_auth(
    api_key: APIKey,
    db: Session,
) -> ApiClient:
    if api_key:
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


def get_root_token(bearer_token: HTTPAuthorizationCredentials = Security(bearer_token)) -> str:
    if bearer_token:
        token = bearer_token.credentials
        if token and token in settings.ROOT_TOKENS:
            return token
    raise OasstError(
        "Could not validate credentials",
        error_code=OasstErrorCode.ROOT_TOKEN_NOT_AUTHORIZED,
        http_status_code=HTTPStatus.FORBIDDEN,
    )


async def user_identifier(request: Request) -> str:
    """Identify a request by user based on api_key and user header"""
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    user = request.headers.get("x-oasst-user")
    if not user:
        payload = await request.json()
        auth_method = payload.get("user").get("auth_method")
        user_id = payload.get("user").get("id")
        user = f"{auth_method}:{user_id}"
    return f"{api_key}:{user}"


class UserRateLimiter(RateLimiter):
    def __init__(
        self, times: int = 100, milliseconds: int = 0, seconds: int = 0, minutes: int = 1, hours: int = 0
    ) -> None:
        super().__init__(times, milliseconds, seconds, minutes, hours, user_identifier)

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


class UserTaskTypeRateLimiter(RateLimiter):
    """
    User-level rate limiter for a specific task type.
    """

    def __init__(
        self,
        task_types: list[str],
        times: int = 100,
        milliseconds: int = 0,
        seconds: int = 0,
        minutes: int = 1,
        hours: int = 0,
    ) -> None:
        super().__init__(times, milliseconds, seconds, minutes, hours, user_identifier)
        self.task_types = task_types

    async def __call__(self, request: Request, response: Response, api_key: str = Depends(get_api_key)) -> None:
        # Skip if rate limiting is disabled
        if not settings.RATE_LIMIT:
            return

        # Attempt to retrieve api_key and user information
        json = await request.json()
        user = json.get("user")

        # Skip when api_key and user information are not available
        # (such that it will be handled by `APIClientRateLimiter`)
        if not api_key or not user or not user.get("id"):
            return

        # Skip when the request is not in our task types of interest
        if not json.get("type") or json.get("type") not in self.task_types:
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
