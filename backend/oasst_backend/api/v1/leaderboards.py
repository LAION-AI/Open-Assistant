from typing import Optional

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.user_stats_repository import UserStatsRepository, UserStatsTimeFrame
from oasst_shared.schemas.protocol import LeaderboardStats
from sqlmodel import Session

router = APIRouter()


@router.get("/{time_frame}")
def get_leaderboard_day(
    time_frame: UserStatsTimeFrame,
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.get_leaderboard(time_frame, limit=max_count)
