import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.api.v1 import utils
from oasst_backend.models import ApiClient, User
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.user_repository import UserRepository
from oasst_backend.user_stats_repository import UserStatsRepository, UserStatsTimeFrame
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/users/{user_id}", response_model=protocol.FrontEndUser)
def get_user(
    user_id: UUID,
    api_client_id: UUID = None,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_api_client),
):
    """
    Get a user by global user ID. Only trusted clients can resolve users they did not register.
    """
    ur = UserRepository(db, api_client)
    user: User = ur.get_user(user_id, api_client_id)
    return user.to_protocol_frontend_user()


@router.put("/users/{user_id}", status_code=HTTP_204_NO_CONTENT)
def update_user(
    user_id: UUID,
    enabled: Optional[bool] = None,
    notes: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
    stats_enabled: Optional[bool] = None,
):
    """
    Update a user by global user ID. Only trusted clients can update users.
    """
    ur = UserRepository(db, api_client)
    ur.update_user(user_id, enabled, notes, stats_enabled)


@router.delete("/users/{user_id}", status_code=HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    """
    Delete a user by global user ID. Only trusted clients can delete users.
    """
    ur = UserRepository(db, api_client)
    ur.mark_user_deleted(user_id)


@router.get("/{user_id}/messages", response_model=list[protocol.Message])
def query_user_messages(
    user_id: UUID,
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
    Query user messages.
    """
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(
        user_id=user_id,
        api_client_id=api_client_id,
        desc=desc,
        limit=max_count,
        start_date=start_date,
        end_date=end_date,
        only_roots=only_roots,
        deleted=None if include_deleted else False,
    )

    return utils.prepare_message_list(messages)


@router.delete("/{user_id}/messages", status_code=HTTP_204_NO_CONTENT)
def mark_user_messages_deleted(
    user_id: UUID, api_client: ApiClient = Depends(deps.get_trusted_api_client), db: Session = Depends(deps.get_db)
):
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(user_id=user_id)
    pr.mark_messages_deleted(messages)


@router.get("/{user_id}/stats", response_model=dict[str, protocol.UserScore | None])
def query_user_stats(
    user_id: UUID,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    usr = UserStatsRepository(db)
    return usr.get_user_stats_all_time_frames(user_id=user_id)


@router.get("/{user_id}/stats/{time_frame}", response_model=protocol.UserScore)
def query_user_stats_timeframe(
    user_id: UUID,
    time_frame: UserStatsTimeFrame,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    usr = UserStatsRepository(db)
    return usr.get_user_stats_all_time_frames(user_id=user_id)[time_frame.value]
