from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.schemas.text_labels import LabelOption, ValidLabelsResponse
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

router = APIRouter()


@router.post("/", status_code=HTTP_204_NO_CONTENT)
def label_text(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    text_labels: protocol_schema.TextLabels,
) -> None:
    """
    Label a piece of text.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        logger.info(f"Labeling text {text_labels=}.")
        pr = PromptRepository(db, api_client, client_user=text_labels.user)
        pr.store_text_labels(text_labels)

    except Exception:
        logger.exception("Failed to store label.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
        )


@router.get("/valid_labels")
def get_valid_lables() -> ValidLabelsResponse:
    return ValidLabelsResponse(
        valid_labels=[
            LabelOption(name=l.value, display_text=l.display_text, help_text=l.help_text)
            for l in protocol_schema.TextLabel
        ]
    )
