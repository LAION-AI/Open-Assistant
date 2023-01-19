from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.models.api_client import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
from oasst_shared.schemas.protocol import SystemStats
from oasst_shared.utils import ScopeTimer

router = APIRouter()


class CreateApiClientRequest(pydantic.BaseModel):
    description: str
    frontend_type: str
    trusted: bool | None = False
    admin_email: str | None = None


@router.post("/api_client")
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


class PurgeResultModel(pydantic.BaseModel):
    before: SystemStats
    after: SystemStats
    preview: bool
    duration: float


@router.post("/purge_user/{user_id}", response_model=PurgeResultModel)
async def purge_user(
    user_id: UUID,
    preview: bool = True,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> str:
    assert api_client.trusted

    @managed_tx_function(CommitMode.NONE if preview else CommitMode.COMMIT)
    def purge_tx(session: deps.Session):
        pr = PromptRepository(session, api_client)

        stats_before = pr.get_stats()

        user = pr.user_repository.get_user(user_id)
        if preview:
            logger.info(
                f"PURGE USER PREVIEW: '{user.display_name}' (id: {str(user_id)}; username: '{user.username}'; auth-method: '{user.auth_method}')"
            )
        else:
            logger.warning(
                f"PURGE USER: '{user.display_name}' (id: {str(user_id)}; username: '{user.username}'; auth-method: '{user.auth_method}')"
            )
        tm = TreeManager(session, pr)
        tm.purge_user(user_id)

        return stats_before, pr.get_stats()

    timer = ScopeTimer()
    before, after = purge_tx()
    timer.stop()
    logger.info(f"{before=}; {after=}")
    return PurgeResultModel(before=before, after=after, preview=preview, duration=timer.elapsed)
