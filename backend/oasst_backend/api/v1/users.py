import datetime
from typing import Callable, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.api.v1 import utils
from oasst_backend.api.v1.messages import get_messages_cursor
from oasst_backend.models import ApiClient, User
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.user_repository import UserRepository
from oasst_backend.user_stats_repository import UserStatsRepository, UserStatsTimeFrame
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/by_username", response_model=list[protocol.FrontEndUser])
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


@router.get("/by_display_name", response_model=list[protocol.FrontEndUser])
def get_users_ordered_by_display_name(
    api_client_id: Optional[UUID] = None,
    gte_display_name: Optional[str] = None,
    gt_id: Optional[UUID] = None,
    lte_display_name: Optional[str] = None,
    lt_id: Optional[UUID] = None,
    auth_method: Optional[str] = None,
    search_text: Optional[str] = None,
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    ur = UserRepository(db, api_client)
    users = ur.query_users_ordered_by_display_name(
        api_client_id=api_client_id,
        gte_display_name=gte_display_name,
        gt_id=gt_id,
        lte_display_name=lte_display_name,
        lt_id=lt_id,
        auth_method=auth_method,
        search_text=search_text,
        limit=max_count,
    )
    return [u.to_protocol_frontend_user() for u in users]


@router.get("/cursor", response_model=protocol.FrontEndUserPage)
def get_users_cursor(
    lt: Optional[str] = None,
    gt: Optional[str] = None,
    sort_key: Optional[str] = Query("username", max_length=32),
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client_id: Optional[UUID] = None,
    search_text: Optional[str] = None,
    auth_method: Optional[str] = None,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    assert max_count is not None

    def split_cursor(x: str | None) -> tuple[str, UUID]:
        if not x:
            return None, None
        m = utils.split_uuid_pattern.match(x)
        if m:
            return m[2], UUID(m[1])
        return x, None

    items: list[protocol.FrontEndUser]
    qry_max_count = max_count + 1 if lt is None or gt is None else max_count

    def get_next_prev(num_rows: int, lt: str | None, gt: str | None, key_fn: Callable[[protocol.FrontEndUser], str]):
        p, n = None, None
        if len(items) > 0:
            if (num_rows > max_count and lt) or gt:
                p = str(items[0].user_id) + "$" + key_fn(items[0])
            if num_rows > max_count or lt:
                n = str(items[-1].user_id) + "$" + key_fn(items[-1])
        else:
            if gt:
                p = gt
            if lt:
                n = lt
        return p, n

    def remove_extra_item(items: list[protocol.FrontEndUser], lt: str | None, gt: str | None):
        num_rows = len(items)
        if qry_max_count > max_count and num_rows == qry_max_count:
            assert not (lt and gt)
            if lt:
                items = items[1:]
            else:
                items = items[:-1]
        return items, num_rows

    n, p = None, None
    if sort_key == "username":
        lte_username, lt_id = split_cursor(lt)
        gte_username, gt_id = split_cursor(gt)
        items = get_users_ordered_by_username(
            api_client_id=api_client_id,
            gte_username=gte_username,
            gt_id=gt_id,
            lte_username=lte_username,
            lt_id=lt_id,
            auth_method=auth_method,
            search_text=search_text,
            max_count=qry_max_count,
            api_client=api_client,
            db=db,
        )
        items, num_rows = remove_extra_item(items, lte_username, gte_username)
        p, n = get_next_prev(num_rows, lte_username, gte_username, lambda x: x.id)

    elif sort_key == "display_name":
        lte_display_name, lt_id = split_cursor(lt)
        gte_display_name, gt_id = split_cursor(gt)
        items = get_users_ordered_by_display_name(
            api_client_id=api_client_id,
            gte_display_name=gte_display_name,
            gt_id=gt_id,
            lte_display_name=lte_display_name,
            lt_id=lt_id,
            auth_method=auth_method,
            search_text=search_text,
            max_count=qry_max_count,
            api_client=api_client,
            db=db,
        )
        items, num_rows = remove_extra_item(items, lte_display_name, gte_display_name)
        p, n = get_next_prev(num_rows, lte_display_name, gte_display_name, lambda x: x.display_name)

    else:
        raise OasstError(f"Unsupported sort key: '{sort_key}'", OasstErrorCode.SORT_KEY_UNSUPPORTED)

    return protocol.FrontEndUserPage(prev=p, next=n, sort_key=sort_key, order="asc", items=items)


@router.get("/{user_id}", response_model=protocol.FrontEndUser)
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


@router.put("/{user_id}", status_code=HTTP_204_NO_CONTENT)
def update_user(
    user_id: UUID,
    enabled: Optional[bool] = None,
    notes: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    """
    Update a user by global user ID. Only trusted clients can update users.
    """
    ur = UserRepository(db, api_client)
    ur.update_user(user_id, enabled, notes)


@router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT)
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
    messages = pr.query_messages_ordered_by_created_date(
        user_id=user_id,
        api_client_id=api_client_id,
        desc=desc,
        limit=max_count,
        gte_created_date=start_date,
        lte_created_date=end_date,
        only_roots=only_roots,
        deleted=None if include_deleted else False,
    )

    return utils.prepare_message_list(messages)


@router.get("/{user_id}/messages/cursor", response_model=protocol.MessagePage)
def query_user_messages_cursor(
    user_id: Optional[UUID],
    lt: Optional[str] = None,
    gt: Optional[str] = None,
    only_roots: Optional[bool] = False,
    include_deleted: Optional[bool] = False,
    max_count: Optional[int] = Query(10, gt=0, le=1000),
    desc: Optional[bool] = False,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    return get_messages_cursor(
        lt=lt,
        gt=gt,
        user_id=user_id,
        only_roots=only_roots,
        include_deleted=include_deleted,
        max_count=max_count,
        desc=desc,
        api_client=api_client,
        db=db,
    )


@router.delete("/{user_id}/messages", status_code=HTTP_204_NO_CONTENT)
def mark_user_messages_deleted(
    user_id: UUID, api_client: ApiClient = Depends(deps.get_trusted_api_client), db: Session = Depends(deps.get_db)
):
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages_ordered_by_created_date(user_id=user_id, limit=None)
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
