from fastapi import APIRouter
from oasst_backend import auth
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()


@router.post("/token", response_model=protocol_schema.Token)
def login_for_access_token(
    *,
    temp,  # TODO
):
    user: ... = auth.authenticate_user(...)  # TODO
    if not user:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    access_token = auth.create_access_token(user)
    return protocol_schema.Token(access_token=access_token, token_type="bearer")
