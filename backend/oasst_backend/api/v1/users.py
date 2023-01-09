import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from oasst_backend.api import deps
from oasst_backend.api.v1 import utils
from oasst_backend.models import ApiClient
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/{user_id}/messages", response_model=list[protocol.Message])
def query_user_messages(
    user_id: UUID,
    api_client_id: UUID = None,
    max_count: int = Query(10, gt=0, le=1000),
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    only_roots: bool = False,
    desc: bool = True,
    include_deleted: bool = False,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Query user messages.
    """
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(
        user_id=user_id,
        api_client_id=api_client_id,
        desc=desc,
        limit=max_count,
        start_date=start_date,
        end_date=end_date,
        only_roots=only_roots,
        deleted=None if include_deleted else False,
    )

    return utils.prepare_message_list(messages)


@router.delete("/{user_id}/messages", status_code=HTTP_204_NO_CONTENT)
def mark_user_messages_deleted(
    user_id: UUID, api_client: ApiClient = Depends(deps.get_trusted_api_client), db: Session = Depends(deps.get_db)
):
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(user_id=user_id)
    pr.mark_messages_deleted(messages)
