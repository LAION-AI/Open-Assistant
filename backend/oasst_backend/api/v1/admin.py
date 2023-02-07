from datetime import datetime
from typing import Optional
from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.config import Settings, settings
from oasst_backend.models import ApiClient, User
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
from oasst_shared.schemas.protocol import SystemStats
from oasst_shared.utils import ScopeTimer, unaware_to_utc

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


@router.post("/admin/flagged_messages/{message_id}/processed", response_model=FlaggedMessageResponse)
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
