# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from oasst_backend.api import deps
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from sqlmodel import Session

router = APIRouter()


@router.get("/")
def get_message_stats(
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_trusted_api_client),
):
    pr = PromptRepository(db, api_client, None)
    return pr.get_stats()
