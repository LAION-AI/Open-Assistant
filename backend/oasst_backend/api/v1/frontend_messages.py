# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from oasst_backend.api import deps
from oasst_backend.api.v1 import utils
from oasst_backend.exceptions import OasstError, OasstErrorCode
from oasst_backend.models import ApiClient
from oasst_backend.models.db_payload import MessagePayload
from oasst_backend.prompt_repository import PromptRepository
from sqlmodel import Session

router = APIRouter()


@router.get("/{message_id}")
def get_message_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a message by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_message_by_frontend_message_id(message_id)

    if not isinstance(message.payload.payload, MessagePayload):
        # Unexpected message payload
        raise OasstError("Invalid message", OasstErrorCode.INVALID_MESSAGE)

    return utils.prepare_message(message)


@router.get("/{message_id}/conversation")
def get_conv_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a conversation from the tree root and up to the message with given frontend ID.
    """

    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_message_by_frontend_message_id(message_id)
    messages = pr.fetch_message_conversation(message)
    return utils.prepare_conversation(messages)


@router.get("/{message_id}/tree")
def get_tree_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    Message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_message_by_frontend_message_id(message_id)
    tree = pr.fetch_message_tree(message.message_tree_id)
    return utils.prepare_tree(tree, message.message_tree_id)


@router.get("/{message_id}/children")
def get_children_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_message_by_frontend_message_id(message_id)
    messages = pr.fetch_message_children(message.id)
    return utils.prepare_message_list(messages)


@router.get("/{message_id}/descendants")
def get_descendants_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a subtree which starts with this message.
    The message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_message_by_frontend_message_id(message_id)
    descendants = pr.fetch_message_descendants(message)
    return utils.prepare_tree(descendants, message.id)


@router.get("/{message_id}/longest_conversation_in_tree")
def get_longest_conv_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get the longest conversation from the tree of the message.
    The message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_message_by_frontend_message_id(message_id)
    conv = pr.fetch_longest_conversation(message.message_tree_id)
    return utils.prepare_conversation(conv)


@router.get("/{message_id}/max_children_in_tree")
def get_max_children_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get message with the most children from the tree of the provided message.
    The message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_message_by_frontend_message_id(message_id)
    message, children = pr.fetch_message_with_max_children(message.message_tree_id)
    return utils.prepare_tree([message, *children], message.id)
