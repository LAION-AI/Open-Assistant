"""Logic related to authorization actions."""

import hashlib
import json
from datetime import datetime, timedelta

import sqlmodel
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from jose import jwe
from jose.exceptions import JWEError
from loguru import logger
from oasst_inference_server import deps, models
from oasst_inference_server.schemas import auth
from oasst_inference_server.settings import settings
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

authorization_scheme = APIKeyHeader(name="Authorization", auto_error=False, scheme_name="Authorization")
refresh_scheme = APIKeyHeader(name="Refresh", auto_error=False, scheme_name="Refresh")

trusted_client_scheme = APIKeyHeader(name="TrustedClient", auto_error=False, scheme_name="TrustedClient")


def get_user_id_from_trusted_client_token(trusted_client_token: str) -> str:
    info: auth.TrustedClient = auth.TrustedClientToken(content=trusted_client_token).content
    if info.api_key not in settings.trusted_api_keys_list:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized client")
    return info.user_id


def get_user_id_from_auth_token(token: str) -> str:
    if token is None or not token.startswith("Bearer "):
        logger.warning(f"Invalid token: {token}")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")

    token = token[len("Bearer ") :]
    if not token:
        logger.warning(f"Invalid token: {token}")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")

    key: bytes = derive_key()

    try:
        token: bytes = jwe.decrypt(token, key)
    except JWEError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")

    payload: dict = json.loads(token.decode())
    validate_access_token(payload)

    user_id = payload.get("user_id")
    return user_id


def get_current_user_id(
    token: str = Security(authorization_scheme), trusted_client_token: str = Security(trusted_client_scheme)
) -> str:
    """Get the current user ID."""
    if trusted_client_token is not None:
        return get_user_id_from_trusted_client_token(trusted_client_token)

    return get_user_id_from_auth_token(token)


def create_access_token(user_id: str) -> str:
    """Create encoded JSON Web Token (JWT) for the given user ID."""
    payload: bytes = build_payload(user_id, "access", settings.auth_access_token_expire_minutes)

    key = derive_key()
    token: bytes = jwe.encrypt(payload, key)

    return token.decode()


async def create_refresh_token(user_id: str) -> str:
    """Create encoded refresh token for the given user ID."""
    payload: bytes = build_payload(user_id, "refresh", settings.auth_refresh_token_expire_minutes)

    key = derive_key()
    token: bytes = jwe.encrypt(payload, key)

    await store_refresh_token(token, user_id)

    return token.decode()


async def refresh_access_token(refresh_token: str) -> str:
    """Refresh the access token using the given refresh token."""
    key: bytes = derive_key()

    try:
        token: bytes = jwe.decrypt(refresh_token, key)
    except JWEError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")

    token_model = await query_refresh_token(token)

    if not token_model or not token_model.enabled:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")

    payload: dict = json.loads(token.decode())
    validate_refresh_token(payload, token_model.user_id)

    user_id = payload.get("user_id")
    access_token: str = create_access_token(user_id)
    return access_token


def derive_key() -> bytes:
    """Derive a key from the auth secret."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=settings.auth_length,
        salt=settings.auth_salt,
        info=settings.auth_info,
    )
    key = hkdf.derive(settings.auth_secret)
    return key


def build_payload(user_id: str, token_type: str, expire_minutes: int) -> bytes:
    """Build a token payload as `bytes` encoded from a JSON string."""
    expires_delta = timedelta(minutes=expire_minutes)
    expire = datetime.utcnow() + expires_delta

    payload_dict = {
        "user_id": user_id,
        "exp": expire.timestamp(),
        "type": token_type,
    }

    payload: bytes = json.dumps(payload_dict).encode()
    return payload


async def store_refresh_token(token: bytes, user_id: str) -> None:
    """Store a refresh token in the backend DB."""
    token_hash: bytes = hashlib.sha256(token).hexdigest()

    async with deps.manual_create_session() as session:
        token_model: models.DbRefreshToken = models.DbRefreshToken(token_hash=token_hash, user_id=user_id)
        session.add(token_model)
        await session.commit()


async def query_refresh_token(token: bytes) -> models.DbRefreshToken | None:
    """Query a refresh token in the backend DB."""
    token_hash: bytes = hashlib.sha256(token).hexdigest()

    async with deps.manual_create_session() as session:
        query = sqlmodel.select(models.DbRefreshToken).where(models.DbRefreshToken.token_hash == token_hash)
        token_model: models.DbRefreshToken = (await session.exec(query)).one_or_none()

    return token_model


def validate_access_token(payload: dict) -> None:
    """Validate an access token payload."""
    user_id = payload.get("user_id")
    exp = payload.get("exp")
    token_type = payload.get("type")

    if not user_id or not exp:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if not token_type or token_type != "access":
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid token type")

    if datetime.utcnow() >= datetime.fromtimestamp(exp):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expired")


def validate_refresh_token(payload: dict, compare_user_id: str) -> None:
    """Validate a refresh token payload and confirm it corresponds to the correct user."""
    user_id = payload.get("user_id")
    exp = payload.get("exp")
    token_type = payload.get("type")

    if not exp or not user_id or user_id != compare_user_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if not token_type or token_type != "refresh":
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid token type")

    if datetime.utcnow() >= datetime.fromtimestamp(exp):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expired")
