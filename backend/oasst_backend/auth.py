from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from oasst_backend.models import AuthenticatedUser
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from sqlmodel import Session
from starlette.status import HTTP_401_UNAUTHORIZED

SECRET = "test"  # TODO: read this from configuration. maybe use an auth manager object to make this cleaner
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def authenticate_user(db: Session, placeholder) -> ...:  # TODO
    user = ...  # TODO: we want to authenticate with discord?
    return user


def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session, token: str) -> AuthenticatedUser:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    user = get_user_by_username(db, username)
    if user is None:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    return user


def get_user_by_username(db: Session, username: str) -> Optional[AuthenticatedUser]:
    user: AuthenticatedUser = db.query(AuthenticatedUser).filter(AuthenticatedUser.username == username).first()

    return user
