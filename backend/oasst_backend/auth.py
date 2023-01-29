from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from oasst_backend.models import Account
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from sqlmodel import Session
from starlette.status import HTTP_401_UNAUTHORIZED

SECRET = "test"  # TODO: read this from configuration. maybe use an auth manager object to make this cleaner
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    # TODO store JWT here?
    return encoded_jwt


def get_current_user(db: Session, token: str) -> Account:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        account_id: UUID = payload.get("sub")
        if account_id is None:
            raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    user = get_account_by_id(db, account_id)
    if user is None:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    return user


def get_account_from_discord_user(db: Session, discord_user: dict) -> Optional[Account]:
    account: Account = (
        db.query(Account)
        .filter(
            Account.provider == "discord",
            Account.provider_account_id == discord_user["id"],
        )
        .first()
    )

    return account


def get_account_by_id(db: Session, id: UUID) -> Optional[Account]:
    account: Account = db.query(Account).filter(Account.id == id).first()
    return account
