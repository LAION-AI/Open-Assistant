from datetime import datetime
from typing import Optional
from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends, Query
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.config import Settings, settings
from oasst_backend.models import ApiClient, User
from oasst_backend.prompt_repository import PromptRepository, UserRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
from oasst_shared import utils
from oasst_shared.exceptions.oasst_api_error import OasstError, OasstErrorCode
from oasst_shared.schemas.protocol import PageResult, SystemStats
from oasst_shared.utils import ScopeTimer, log_timing, unaware_to_utc
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


class CreateApiClientRequest(pydantic.BaseModel):
    description: str
    frontend_type: str
    trusted: bool | None = False
    admin_email: str | None = None


@router.post("/api_client", response_model=str)
async def create_api_client(
    request: CreateApiClientRequest,
    root_token: str = Depends(deps.get_root_token),
    session: deps.Session = Depends(deps.get_db),
) -> str:
    logger.info(f"Creating new api client with {request=}")
    api_client = deps.create_api_client(
        session=session,
        description=request.description,
        frontend_type=request.frontend_type,
        trusted=request.trusted,
        admin_email=request.admin_email,
    )
    logger.info(f"Created api_client with key {api_client.api_key}")
    return api_client.api_key


@router.get("/backend_settings/full", response_model=Settings)
async def get_backend_settings_full(api_client: ApiClient = Depends(deps.get_trusted_api_client)) -> Settings:
    logger.info(
        f"Backend settings requested by trusted api_client {api_client.id} (admin_email: {api_client.admin_email}, frontend_type: {api_client.frontend_type})"
    )
    return settings


class PublicSettings(pydantic.BaseModel):
    """Subset of backend settings which can be retrieved by untrusted API clients."""

    PROJECT_NAME: str
    API_V1_STR: str
    MESSAGE_SIZE_LIMIT: int
    DEBUG_USE_SEED_DATA: bool
    DEBUG_ALLOW_SELF_LABELING: bool
    DEBUG_SKIP_EMBEDDING_COMPUTATION: bool
    DEBUG_SKIP_TOXICITY_CALCULATION: bool
    DEBUG_DATABASE_ECHO: bool
    USER_STATS_INTERVAL_DAY: int
    USER_STATS_INTERVAL_WEEK: int
    USER_STATS_INTERVAL_MONTH: int
    USER_STATS_INTERVAL_TOTAL: int


@router.get("/backend_settings/public", response_model=PublicSettings)
async def get_backend_settings_public(api_client: ApiClient = Depends(deps.get_api_client)) -> PublicSettings:
    return PublicSettings(**settings.dict())


class PurgeResultModel(pydantic.BaseModel):
    before: SystemStats
    after: SystemStats
    preview: bool
    duration: float


@router.post("/purge_user/{user_id}", response_model=PurgeResultModel)
async def purge_user(
    user_id: UUID,
    preview: bool = True,
    ban: bool = True,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> str:
    assert api_client.trusted

    @managed_tx_function(CommitMode.ROLLBACK if preview else CommitMode.COMMIT)
    def purge_tx(session: deps.Session) -> tuple[User, SystemStats, SystemStats]:
        pr = PromptRepository(session, api_client)

        stats_before = pr.get_stats()

        user = pr.user_repository.get_user(user_id)
        tm = TreeManager(session, pr)
        tm.purge_user(user_id=user_id, ban=ban)

        session.expunge(user)
        return user, stats_before, pr.get_stats()

    timer = ScopeTimer()
    user, before, after = purge_tx()
    timer.stop()

    if preview:
        logger.info(
            f"PURGE USER PREVIEW: '{user.display_name}' (id: {str(user_id)}; username: '{user.username}'; auth-method: '{user.auth_method}')"
        )
    else:
        logger.warning(
            f"PURGE USER: '{user.display_name}' (id: {str(user_id)}; username: '{user.username}'; auth-method: '{user.auth_method}')"
        )

    logger.info(f"{before=}; {after=}")
    return PurgeResultModel(before=before, after=after, preview=preview, duration=timer.elapsed)


@router.post("/purge_user/{user_id}/messages", response_model=PurgeResultModel)
async def purge_user_messages(
    user_id: UUID,
    purge_initial_prompts: bool = False,
    min_date: datetime = None,
    max_date: datetime = None,
    preview: bool = True,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> str:
    assert api_client.trusted

    min_date = unaware_to_utc(min_date)
    max_date = unaware_to_utc(max_date)

    @managed_tx_function(CommitMode.ROLLBACK if preview else CommitMode.COMMIT)
    def purge_user_messages_tx(session: deps.Session):
        pr = PromptRepository(session, api_client)

        stats_before = pr.get_stats()

        user = pr.user_repository.get_user(user_id)

        tm = TreeManager(session, pr)
        tm.purge_user_messages(
            user_id, purge_initial_prompts=purge_initial_prompts, min_date=min_date, max_date=max_date
        )

        session.expunge(user)
        return user, stats_before, pr.get_stats()

    timer = ScopeTimer()
    user, before, after = purge_user_messages_tx()
    timer.stop()

    if preview:
        logger.info(
            f"PURGE USER MESSAGES PREVIEW: '{user.display_name}' (id: {str(user_id)}; username: '{user.username}'; auth-method: '{user.auth_method}')"
        )
    else:
        logger.warning(
            f"PURGE USER MESSAGES: '{user.display_name}' (id: {str(user_id)}; username: '{user.username}'; auth-method: '{user.auth_method}')"
        )

    logger.info(f"{before=}; {after=}")
    return PurgeResultModel(before=before, after=after, preview=preview, duration=timer.elapsed)


class FlaggedMessageResponse(pydantic.BaseModel):
    message_id: UUID
    processed: bool
    created_date: Optional[datetime]


class FlaggedMessagePage(PageResult):
    items: list[FlaggedMessageResponse]


@router.get("/flagged_messages/cursor", response_model=FlaggedMessagePage)
def get_flagged_messages_cursor(
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    max_count: Optional[int] = Query(10, gt=0, le=1000),
    desc: Optional[bool] = False,
    session: deps.Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> str:
    assert api_client.trusted
    assert max_count is not None

    def split_cursor(x: str | None) -> tuple[datetime, UUID]:
        if not x:
            return None, None
        try:
            m = utils.split_uuid_pattern.match(x)
            if m:
                return datetime.fromisoformat(m[2]), UUID(m[1])
            return datetime.fromisoformat(x), None
        except ValueError:
            raise OasstError("Invalid cursor value", OasstErrorCode.INVALID_CURSOR_VALUE)

    if desc:
        gte_created_date, gt_id = split_cursor(before)
        lte_created_date, lt_id = split_cursor(after)
        query_desc = not (before is not None and not after)
    else:
        lte_created_date, lt_id = split_cursor(before)
        gte_created_date, gt_id = split_cursor(after)
        query_desc = before is not None and not after

    logger.debug(f"{desc=} {query_desc=} {gte_created_date=} {lte_created_date=}")

    qry_max_count = max_count + 1 if before is None or after is None else max_count

    pr = PromptRepository(session, api_client)
    items = pr.fetch_flagged_messages_by_created_date(
        gte_created_date=gte_created_date,
        gt_id=gt_id,
        lte_created_date=lte_created_date,
        lt_id=lt_id,
        desc=query_desc,
        limit=qry_max_count,
    )

    num_rows = len(items)
    if qry_max_count > max_count and num_rows == qry_max_count:
        assert not (before and after)
        items = items[:-1]

    if desc != query_desc:
        items.reverse()

    n, p = None, None
    if len(items) > 0:
        if (num_rows > max_count and before) or after:
            p = str(items[0].message_id) + "$" + items[0].created_date.isoformat()
        if num_rows > max_count or before:
            n = str(items[-1].message_id) + "$" + items[-1].created_date.isoformat()
    else:
        if after:
            p = lte_created_date.isoformat() if desc else gte_created_date.isoformat()
        if before:
            n = gte_created_date.isoformat() if desc else lte_created_date.isoformat()

    order = "desc" if desc else "asc"
    print(p, n, items, order)
    return FlaggedMessagePage(prev=p, next=n, sort_key="created_date", order=order, items=items)


@router.get("/flagged_messages", response_model=list[FlaggedMessageResponse])
async def get_flagged_messages(
    max_count: Optional[int],
    session: deps.Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> str:
    assert api_client.trusted

    pr = PromptRepository(session, api_client)
    flagged_messages = pr.fetch_flagged_messages(max_count=max_count)
    resp = [FlaggedMessageResponse(**msg.__dict__) for msg in flagged_messages]
    return resp


@router.post("/flagged_messages/{message_id}/processed", response_model=FlaggedMessageResponse)
async def process_flagged_messages(
    message_id: UUID,
    session: deps.Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> str:
    assert api_client.trusted

    pr = PromptRepository(session, api_client)
    flagged_msg = pr.process_flagged_message(message_id=message_id)
    resp = FlaggedMessageResponse(**flagged_msg.__dict__)
    return resp


class MergeUsersRequest(pydantic.BaseModel):
    destination_user_id: UUID
    source_user_ids: list[UUID]


@log_timing(level="INFO")
@router.post("/merge_users", response_model=None, status_code=HTTP_204_NO_CONTENT)
def merge_users(
    request: MergeUsersRequest,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> None:
    @managed_tx_function(CommitMode.COMMIT)
    def merge_users_tx(session: deps.Session):
        ur = UserRepository(session, api_client)
        ur.merge_users(destination_user_id=request.destination_user_id, source_user_ids=request.source_user_ids)

    merge_users_tx()

    logger.info(f"Merged users: {request=}")
