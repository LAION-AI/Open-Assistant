import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.api.v1 import utils
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.user_repository import UserRepository
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/", response_model=list[protocol.User])
def get_users(
    api_client_id: UUID = None,
    max_count: int = Query(10, gt=0, le=20),  # TODO: refine bounds
    gte: str = None,
    lt: str = None,
    auth_method: str = None,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    pr = UserRepository(db, api_client)
    users = pr.query_users(api_client_id=api_client_id, limit=max_count, gte=gte, lt=lt, auth_method=auth_method)
    return [u.to_protocol_user() for u in users]


@router.get("/{auth_method}/{username}", response_model=protocol.FrontEndUser)
def query_frontend_user(
    auth_method: str,
    username: str,
    api_client_id: Optional[UUID] = None,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Query frontend user.
    """
    ur = UserRepository(db, api_client)
    user = ur.query_frontend_user(auth_method, username, api_client_id)
    return protocol.FrontEndUser(
        id=user.username, display_name=user.display_name, auth_method=user.auth_method, user_id=user.id
    )


@router.get("/{auth_method}/{username}/messages", response_model=list[protocol.Message])
def query_frontend_user_messages(
    auth_method: str,
    username: str,
    api_client_id: UUID = None,
    max_count: int = Query(10, gt=0, le=1000),
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    only_roots: bool = False,
    desc: bool = True,
    include_deleted: bool = False,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Query frontend user messages.
    """
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(
        auth_method=auth_method,
        username=username,
        api_client_id=api_client_id,
        desc=desc,
        limit=max_count,
        start_date=start_date,
        end_date=end_date,
        only_roots=only_roots,
        deleted=None if include_deleted else False,
    )
    return utils.prepare_message_list(messages)


@router.delete("/{auth_method}/{username}/messages", status_code=HTTP_204_NO_CONTENT)
def mark_frontend_user_messages_deleted(
    auth_method: str,
    username: str,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
    db: Session = Depends(deps.get_db),
):
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(auth_method=auth_method, username=username, api_client_id=api_client.id)
    pr.mark_messages_deleted(messages)
