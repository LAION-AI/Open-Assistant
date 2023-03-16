from fastapi import APIRouter, Depends
from oasst_backend.api import deps
from oasst_backend.cached_stats_repository import CachedStatsRepository
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.tree_manager import TreeManager, TreeManagerStats, TreeMessageCountStats
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/", response_model=protocol.SystemStats)
def get_message_stats(
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    pr = PromptRepository(db, api_client)
    return pr.get_stats()


@router.get("/tree_manager/state_counts", response_model=dict[str, int])
def get_tree_manager__state_counts(
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    pr = PromptRepository(db, api_client)
    tm = TreeManager(db, pr)
    return tm.tree_counts_by_state()


@router.get("/tree_manager/message_counts", response_model=list[TreeMessageCountStats])
def get_tree_manager__message_counts(
    only_active: bool = True,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    pr = PromptRepository(db, api_client)
    tm = TreeManager(db, pr)
    return tm.tree_message_count_stats(only_active=only_active)


@router.get("/tree_manager", response_model=TreeManagerStats)
def get_tree_manager__stats(
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    pr = PromptRepository(db, api_client)
    tm = TreeManager(db, pr)
    return tm.stats()


@router.get("/cached/{name}", response_model=protocol.CachedStatsResponse)
def get_cached_stats(
    *,
    name: protocol.CachedStatsName,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_api_client),
):
    csr = CachedStatsRepository(db)
    return csr.get_stats(name)


@router.get("/cached", response_model=protocol.AllCachedStatsResponse)
def get_cached_stats_all(
    *,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_api_client),
):
    csr = CachedStatsRepository(db)
    return csr.get_stats_all()


@router.post("/cached/update", response_model=None, status_code=HTTP_204_NO_CONTENT)
def update_cached_stats(
    *,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    @managed_tx_function(CommitMode.COMMIT)
    def update_tx(db: deps.Session) -> None:
        csr = CachedStatsRepository(db)
        csr.update_all_cached_stats()

    update_tx()
