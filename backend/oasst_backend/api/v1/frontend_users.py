import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.api.v1 import utils
from oasst_backend.api.v1.messages import get_messages_cursor
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.user_repository import UserRepository
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/", response_model=list[protocol.FrontEndUser], deprecated=True)
def get_users_ordered_by_username(
    api_client_id: Optional[UUID] = None,
    gte_username: Optional[str] = None,
    gt_id: Optional[UUID] = None,
    lte_username: Optional[str] = None,
    lt_id: Optional[UUID] = None,
    search_text: Optional[str] = None,
    auth_method: Optional[str] = None,
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    ur = UserRepository(db, api_client)
    users = ur.query_users_ordered_by_username(
        api_client_id=api_client_id,
        gte_username=gte_username,
        gt_id=gt_id,
        lte_username=lte_username,
        lt_id=lt_id,
        auth_method=auth_method,
        search_text=search_text,
        limit=max_count,
    )
    return [u.to_protocol_frontend_user() for u in users]


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
    return user.to_protocol_frontend_user()


@router.post("/", response_model=protocol.FrontEndUser)
def create_frontend_user(
    *,
    create_user: protocol.CreateFrontendUserRequest,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    ur = UserRepository(db, api_client)
    user = ur.lookup_client_user(create_user, create_missing=True)

    def changed(a, b) -> bool:
        return a is not None and a != b

    # only call update_user if something changed
    if (
        changed(create_user.enabled, user.enabled)
        or changed(create_user.show_on_leaderboard, user.show_on_leaderboard)
        or changed(create_user.notes, user.notes)
        or (create_user.tos_acceptance and user.tos_acceptance_date is None)
    ):
        user = ur.update_user(
            user.id,
            enabled=create_user.enabled,
            show_on_leaderboard=create_user.show_on_leaderboard,
            tos_acceptance=create_user.tos_acceptance,
            notes=create_user.notes,
        )

    return user.to_protocol_frontend_user()


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
    lang: Optional[str] = None,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Query frontend user messages.
    """
    pr = PromptRepository(db, api_client, auth_method=auth_method, username=username)
    messages = pr.query_messages_ordered_by_created_date(
        auth_method=auth_method,
        username=username,
        api_client_id=api_client_id,
        desc=desc,
        limit=max_count,
        gte_created_date=start_date,
        lte_created_date=end_date,
        only_roots=only_roots,
        deleted=None if include_deleted else False,
        lang=lang,
    )
    return utils.prepare_message_list(messages)


@router.get("/{auth_method}/{username}/messages/cursor", response_model=protocol.MessagePage)
def query_frontend_user_messages_cursor(
    auth_method: str,
    username: str,
    before: Optional[str] = None,
    after: Optional[str] = None,
    only_roots: Optional[bool] = False,
    include_deleted: Optional[bool] = False,
    max_count: Optional[int] = Query(10, gt=0, le=1000),
    desc: Optional[bool] = False,
    lang: Optional[str] = None,
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    return get_messages_cursor(
        before=before,
        after=after,
        auth_method=auth_method,
        username=username,
        only_roots=only_roots,
        include_deleted=include_deleted,
        max_count=max_count,
        desc=desc,
        lang=lang,
        frontend_user=frontend_user,
        api_client=api_client,
        db=db,
    )


@router.delete("/{auth_method}/{username}/messages", status_code=HTTP_204_NO_CONTENT)
def mark_frontend_user_messages_deleted(
    auth_method: str,
    username: str,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
    db: Session = Depends(deps.get_db),
):
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages_ordered_by_created_date(
        auth_method=auth_method,
        username=username,
        api_client_id=api_client.id,
        limit=None,
    )
    pr.mark_messages_deleted(messages)
