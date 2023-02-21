from typing import Optional

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.user_stats_repository import UserStatsRepository, UserStatsTimeFrame
from oasst_shared.schemas.protocol import TrollboardStats
from sqlmodel import Session

router = APIRouter()


@router.get("/{time_frame}", response_model=TrollboardStats)
def get_trollboard(
    time_frame: UserStatsTimeFrame,
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    enabled: Optional[bool] = None,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
    db: Session = Depends(deps.get_db),
) -> TrollboardStats:
    usr = UserStatsRepository(db)
    return usr.get_trollboard(time_frame, limit=max_count, enabled=enabled)
