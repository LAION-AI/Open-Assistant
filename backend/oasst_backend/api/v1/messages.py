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


@router.get("/", response_model=list[protocol.Message])
def query_messages(
    username: str = None,
    api_client_id: str = None,
    max_count: int = Query(10, gt=0, le=1000),
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    only_roots: bool = False,
    desc: bool = True,
    allow_deleted: bool = False,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Query messages.
    """
    pr = PromptRepository(db, api_client)
    messages = pr.query_messages(
        username=username,
        api_client_id=api_client_id,
        desc=desc,
        limit=max_count,
        start_date=start_date,
        end_date=end_date,
        only_roots=only_roots,
        deleted=None if allow_deleted else False,
    )

    return utils.prepare_message_list(messages)


@router.get("/{message_id}", response_model=protocol.Message)
def get_message(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a message by its internal ID.
    """
    pr = PromptRepository(db, api_client)
    message = pr.fetch_message(message_id)
    return utils.prepare_message(message)


@router.get("/{message_id}/conversation", response_model=protocol.Conversation)
def get_conv(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a conversation from the tree root and up to the message with given internal ID.
    """

    pr = PromptRepository(db, api_client)
    messages = pr.fetch_message_conversation(message_id)
    return utils.prepare_conversation(messages)


@router.get("/{message_id}/tree", response_model=protocol.MessageTree)
def get_tree(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client)
    message = pr.fetch_message(message_id)
    tree = pr.fetch_message_tree(message.message_tree_id)
    return utils.prepare_tree(tree, message.message_tree_id)


@router.get("/{message_id}/children", response_model=list[protocol.Message])
def get_children(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client)
    messages = pr.fetch_message_children(message_id)
    return utils.prepare_message_list(messages)


@router.get("/{message_id}/descendants", response_model=protocol.MessageTree)
def get_descendants(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a subtree which starts with this message.
    """
    pr = PromptRepository(db, api_client)
    message = pr.fetch_message(message_id)
    descendants = pr.fetch_message_descendants(message)
    return utils.prepare_tree(descendants, message.id)


@router.get("/{message_id}/longest_conversation_in_tree", response_model=protocol.Conversation)
def get_longest_conv(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get the longest conversation from the tree of the message.
    """
    pr = PromptRepository(db, api_client)
    message = pr.fetch_message(message_id)
    conv = pr.fetch_longest_conversation(message.message_tree_id)
    return utils.prepare_conversation(conv)


@router.get("/{message_id}/max_children_in_tree", response_model=protocol.MessageTree)
def get_max_children(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get message with the most children from the tree of the provided message.
    """
    pr = PromptRepository(db, api_client)
    message = pr.fetch_message(message_id)
    message, children = pr.fetch_message_with_max_children(message.message_tree_id)
    return utils.prepare_tree([message, *children], message.id)


@router.delete("/{message_id}", status_code=HTTP_204_NO_CONTENT)
def mark_message_deleted(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_trusted_api_client), db: Session = Depends(deps.get_db)
):
    pr = PromptRepository(db, api_client)
    pr.mark_messages_deleted(message_id)
