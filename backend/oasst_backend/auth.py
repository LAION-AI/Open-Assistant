from datetime import datetime, timedelta

from jose import JWTError, jwt
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from starlette.status import HTTP_401_UNAUTHORIZED

SECRET = "test"  # TODO: read this from configuration. maybe use an auth manager object to make this cleaner
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def authenticate_user(placeholder):  # TODO
    user = ...  # TODO: we want to authenticate with discord?
    return user


def create_access_token(data: dict):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    user = get_user_by_username(
        username
    )  # TODO: how do we get the user here? is discord auth the only option or can we have tokens from non-discord users?
    if user is None:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    return user


def get_user_by_username(username: str):
    # TODO: how do we get the user here?
    # if discord auth is the only option, are we adding a 'discord_username' field to the user model in the db?
    # if so we need to link the discord user to the db user on first time authentication with discord
    # if discord auth is not the only option does it get more complicated?
    pass
