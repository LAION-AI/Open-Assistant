from fastapi import APIRouter, Depends
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.user_repository import UserRepository
from oasst_shared.schemas.protocol import LeaderboardStats
from sqlmodel import Session

router = APIRouter()


@router.get("/create/assistant")
def get_assistant_leaderboard(
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> LeaderboardStats:
    ur = UserRepository(db, api_client)
    return ur.get_user_leaderboard(role="assistant")


@router.get("/create/prompter")
def get_prompter_leaderboard(
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
) -> LeaderboardStats:
    ur = UserRepository(db, api_client)
    return ur.get_user_leaderboard(role="prompter")
