from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.config import settings
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_backend.schemas.text_labels import LabelDescription, ValidLabelsResponse
from oasst_backend.utils.database_utils import CommitMode, managed_tx_function
from oasst_shared.exceptions import OasstError
from oasst_shared.schemas import protocol as protocol_schema
from oasst_shared.schemas.protocol import TextLabel
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

router = APIRouter()


@router.post("/", status_code=HTTP_204_NO_CONTENT)
def label_text(
    *,
    api_key: APIKey = Depends(deps.get_api_key),
    text_labels: protocol_schema.TextLabels,
) -> None:
    """
    Label a piece of text.
    """

    @managed_tx_function(CommitMode.COMMIT)
    def store_text_labels(session: deps.Session):
        api_client = deps.api_auth(api_key, session)
        pr = PromptRepository(session, api_client, client_user=text_labels.user)
        pr.store_text_labels(text_labels)

    try:
        logger.info(f"Labeling text {text_labels=}.")
        store_text_labels()

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to store label.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
        )


@router.get("/valid_labels")
def get_valid_lables(
    *,
    message_id: Optional[UUID] = None,
    db: Session = Depends(deps.get_db),
    api_client: ApiClient = Depends(deps.get_api_client),
) -> ValidLabelsResponse:
    if message_id:
        pr = PromptRepository(db, api_client=api_client)
        message = pr.fetch_message(message_id=message_id)
        if message.parent_id is None:
            valid_labels = settings.tree_manager.labels_initial_prompt
        elif message.role == "assistant":
            valid_labels = settings.tree_manager.labels_assistant_reply
        else:
            valid_labels = settings.tree_manager.labels_prompter_reply
    else:
        valid_labels = [l for l in TextLabel if l != TextLabel.fails_task]

    return ValidLabelsResponse(
        valid_labels=[
            LabelDescription(name=l.value, widget=l.widget.value, display_text=l.display_text, help_text=l.help_text)
            for l in valid_labels
        ]
    )


@router.get("/report_labels")
def get_report_lables() -> ValidLabelsResponse:
    report_labels = [
        TextLabel.spam,
        TextLabel.not_appropriate,
        TextLabel.pii,
        TextLabel.hate_speech,
        TextLabel.sexual_content,
        TextLabel.moral_judgement,
        TextLabel.political_content,
        TextLabel.toxicity,
        TextLabel.violence,
        TextLabel.quality,
    ]
    return ValidLabelsResponse(
        valid_labels=[
            LabelDescription(name=l.value, widget=l.widget.value, display_text=l.display_text, help_text=l.help_text)
            for l in report_labels
        ]
    )
