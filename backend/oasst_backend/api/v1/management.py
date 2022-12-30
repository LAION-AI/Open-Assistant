# -*- coding: utf-8 -*-
import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from oasst_backend.api import deps
from oasst_backend.exceptions import OasstError, OasstErrorCode
from oasst_backend.models import ApiClient, Post
from oasst_backend.models.db_payload import PostPayload
from oasst_backend.prompt_repository import PromptRepository
from oasst_shared.schemas import protocol
from sqlmodel import Session
from starlette.status import HTTP_200_OK

router = APIRouter()


def _prepare_conversation(messages: list[Post]) -> protocol.Conversation:
    conv_messages = []
    for message in messages:
        if not isinstance(message.payload.payload, PostPayload):
            raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        conv_messages.append(
            protocol.ConversationMessage(text=message.payload.payload.text, is_assistant=(message.role == "assistant"))
        )

    return protocol.Conversation(messages=conv_messages)


def _prepare_tree(tree: list[Post], tree_id: UUID) -> protocol.MessageTree:
    tree_messages = []
    for message in tree:
        if not isinstance(message.payload.payload, PostPayload):
            raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        tree_messages.append(
            protocol.Message(
                id=message.id,
                parent_id=message.parent_id,
                text=message.payload.payload.text,
                is_assistant=(message.role == "assistant"),
            )
        )

    return protocol.MessageTree(id=tree_id, messages=tree_messages)


@router.get("/message")
def query_messages(
    username: str = None,
    api_client_id: str = None,
    max_count: int = Query(10, gt=0, le=25),
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    only_roots: bool = False,
    desc: bool = True,
    api_client: ApiClient = Depends(deps.get_api_client),
    db: Session = Depends(deps.get_db),
):
    """
    Query messages.
    """
    if not api_client.trusted and (api_client_id != api_client.id):
        # Unprivileged api client asks for foreign messages
        return []

    pr = PromptRepository(db, api_client, user=None)
    messages = pr.query_messages(
        username=username,
        api_client_id=api_client_id,
        desc=desc,
        max_count=max_count,
        start_date=start_date,
        end_date=end_date,
        only_roots=only_roots,
    )

    return [
        protocol.Message(
            id=m.id, parent_id=m.parent_id, text=m.payload.payload.text, is_assistant=(m.role == "assistant")
        )
        for m in messages
    ]


@router.get("/message/{message_id}")
def get_message(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a message by its internal ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    post = pr.fetch_post(message_id)
    if not isinstance(post.payload.payload, PostPayload):
        raise OasstError("Invalid message id", OasstErrorCode.INVALID_POST_ID)

    return protocol.ConversationMessage(text=post.payload.payload.text, is_assistant=(post.role == "assistant"))


@router.get("/frontend_message/{message_id}")
def get_message_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a message by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post_by_frontend_post_id(message_id, fail_if_missing=True)

    if not isinstance(message.payload.payload, PostPayload):
        raise OasstError("Invalid message id", OasstErrorCode.INVALID_POST_ID)

    return protocol.ConversationMessage(text=message.payload.payload.text, is_assistant=(message.role == "assistant"))


@router.get("/message/{message_id}/conversation")
def get_conv(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a conversation from the tree root and up to the message with given internal ID.
    """

    pr = PromptRepository(db, api_client, user=None)
    messages = pr.fetch_message_conversation(message_id)
    return _prepare_conversation(messages)


@router.get("/frontend_message/{message_id}/conversation")
def get_conv_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a conversation from the tree root and up to the message with given frontend ID.
    """

    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post_by_frontend_post_id(message_id)
    messages = pr.fetch_message_conversation(message)
    return _prepare_conversation(messages)


@router.get("/message/{message_id}/tree")
def get_tree(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post(message_id)
    tree = pr.fetch_message_tree(message)
    return _prepare_tree(tree, message.thread_id)


@router.get("/frontend_message/{message_id}/tree")
def get_tree_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    Message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post_by_frontend_post_id(message_id)
    tree = pr.fetch_message_tree(message)
    return _prepare_tree(tree, message.thread_id)


@router.get("/message/{message_id}/children")
def get_children(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client, user=None)
    return pr.fetch_message_children(message_id)


@router.get("/frontend_message/{message_id}/children")
def get_children_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get all messages belonging to the same message tree.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post_by_frontend_post_id(message_id)
    return pr.fetch_message_children(message)


@router.get("/message/{message_id}/descendants")
def get_descendants(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a subtree which starts with this message.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post(message_id)
    descendants = pr.fetch_post_descendants(message)
    return _prepare_tree(descendants, message.id)


@router.get("/frontend_message/{message_id}/descendants")
def get_descendants_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get a subtree which starts with this message.
    The message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post_by_frontend_post_id(message_id)
    descendants = pr.fetch_post_descendants(message)
    return _prepare_tree(descendants, message.id)


@router.get("/message/{message_id}/longest_conversation_in_tree")
def get_longest_conv(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get the longest conversation from the tree of the message.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post(message_id)
    conv = pr.fetch_longest_conversation(message.thread_id)
    return _prepare_conversation(conv)


@router.get("/frontend_message/{message_id}/longest_conversation_in_tree")
def get_longest_conv_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get the longest conversation from the tree of the message.
    The message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post_by_frontend_post_id(message_id)
    conv = pr.fetch_longest_conversation(message.thread_id)
    return _prepare_conversation(conv)


@router.get("/message/{message_id}/max_children_in_tree")
def get_max_children(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get message with the most children from the tree of the provided message.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post(message_id)
    message, children = pr.fetch_message_with_max_children(message.thread_id)
    return _prepare_tree([message, *children], message.id)


@router.get("/frontend_message/{message_id}/max_children_in_tree")
def get_max_children_by_frontend_id(
    message_id: str, api_client: ApiClient = Depends(deps.get_api_client), db: Session = Depends(deps.get_db)
):
    """
    Get message with the most children from the tree of the provided message.
    The message is identified by its frontend ID.
    """
    pr = PromptRepository(db, api_client, user=None)
    message = pr.fetch_post_by_frontend_post_id(message_id)
    message, children = pr.fetch_message_with_max_children(message.thread_id)
    return _prepare_tree([message, *children], message.id)


@router.delete("/message/{message_id}")
def mark_message_deleted(
    message_id: UUID, api_client: ApiClient = Depends(deps.get_trusted_api_client), db: Session = Depends(deps.get_db)
):
    pr = PromptRepository(db, api_client, None)
    pr.mark_messages_deleted(message_id)
    return Response(status_code=HTTP_200_OK)


@router.delete("/user/{username}/message")
def mark_user_messages_deleted(
    username: str, api_client: ApiClient = Depends(deps.get_trusted_api_client), db: Session = Depends(deps.get_db)
):
    pr = PromptRepository(db, api_client, None)
    messages = pr.query_messages(username=username, api_client_id=api_client.id)
    pr.mark_messages_deleted(messages)
    return Response(status_code=HTTP_200_OK)
