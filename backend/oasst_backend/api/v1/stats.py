from fastapi import APIRouter, Depends
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas import protocol
from sqlmodel import Session

router = APIRouter()


@router.get("/", response_model=protocol.SystemStats)
def get_message_stats(
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    pr = PromptRepository(db, api_client)
    return pr.get_stats()
