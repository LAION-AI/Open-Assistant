# -*- coding: utf-8 -*-
import pydantic
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()


class LabelTextRequest(pydantic.BaseModel):
    text_labels: protocol_schema.TextLabels
    user: protocol_schema.User


@router.post("/")
def label_text(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    request: LabelTextRequest,
) -> None:
    """
    Label a piece of text.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        logger.info(f"Labeling text {request=}.")
        pr = PromptRepository(db, api_client, user=request.user)
        pr.store_text_labels(request.text_labels)

    except Exception:
        logger.exception("Failed to store label.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
        )
