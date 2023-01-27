from typing import Optional

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.user_stats_repository import UserStatsRepository, UserStatsTimeFrame
from oasst_shared.schemas.protocol import LeaderboardStats
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/{time_frame}", response_model=LeaderboardStats)
def get_leaderboard(
    time_frame: UserStatsTimeFrame,
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.get_leaderboard(time_frame, limit=max_count)


@router.post("/update/{time_frame}", response_model=None, status_code=HTTP_204_NO_CONTENT)
def update_leaderboard_time_frame(
    time_frame: UserStatsTimeFrame,
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.update_stats(time_frame=time_frame)


@router.post("/update", response_model=None, status_code=HTTP_204_NO_CONTENT)
def update_leaderboards_all(
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.update_all_time_frames()
