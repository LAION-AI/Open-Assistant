from typing import Optional

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.user_stats_repository import UserStatsRepository, UserStatsTimeFrame
from oasst_shared.schemas.protocol import LeaderboardStats
from sqlmodel import Session

router = APIRouter()


@router.get("/day")
def get_leaderboard_day(
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.get_leader_board(UserStatsTimeFrame.day, limit=max_count)


@router.get("/week")
def get_leaderboard_week(
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.get_leader_board(UserStatsTimeFrame.week, limit=max_count)


@router.get("/month")
def get_leaderboard_month(
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.get_leader_board(UserStatsTimeFrame.month, limit=max_count)


@router.get("/total")
def get_leaderboard_total(
    max_count: Optional[int] = Query(100, gt=0, le=10000),
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
) -> LeaderboardStats:
    usr = UserStatsRepository(db)
    return usr.get_leader_board(UserStatsTimeFrame.total, limit=max_count)
