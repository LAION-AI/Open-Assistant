from fastapi import APIRouter, Depends
from oasst_backend import auth
from oasst_backend.api import deps
from oasst_backend.models import Account
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()


@router.post("/token", response_model=protocol_schema.Token)
def login_for_access_token(
    *,
    temp,  # TODO
    db: Session = Depends(deps.get_db),  #
):
    account: Account = auth.authenticate_user(...)  # TODO
    if not account:
        raise OasstError("Invalid authentication", OasstErrorCode.INVALID_AUTHENTICATION, HTTP_401_UNAUTHORIZED)
    access_token = auth.create_access_token(account)
    return protocol_schema.Token(access_token=access_token, token_type="bearer")
