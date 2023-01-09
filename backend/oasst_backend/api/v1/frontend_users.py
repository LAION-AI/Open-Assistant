import datetime
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
    max_count: int = Query(10, gt=0, le=20),  # TODO: refine bounds
    ge: str = None,
    lt: str = None,
    auth_method: str = None,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    pr = UserRepository(db, api_client)
    users = pr.query_users(limit=max_count, ge=ge, lt=lt, auth_method=auth_method)
    return [utils.prepare_user(u) for u in users]


@router.get("/{username}/messages", response_model=list[protocol.Message])
def query_frontend_user_messages(
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


@router.delete("/{username}/messages", status_code=HTTP_204_NO_CONTENT)
def mark_frontend_user_messages_deleted(
    username: str, api_client: ApiClient = Depends(deps.get_trusted_api_client), db: Session = Depends(deps.get_db)
):
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(username=username, api_client_id=api_client.id)
    pr.mark_messages_deleted(messages)
