# -*- coding: utf-8 -*-

from http import HTTPStatus
from uuid import UUID

from oasst_backend.exceptions import OasstError, OasstErrorCode
from oasst_backend.models import Post
from oasst_backend.models.db_payload import PostPayload
from oasst_shared.schemas import protocol


def prepare_conversation(messages: list[Post]) -> protocol.Conversation:
    conv_messages = []
    for message in messages:
        if not isinstance(message.payload.payload, PostPayload):
            raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        conv_messages.append(
            protocol.ConversationMessage(text=message.payload.payload.text, is_assistant=(message.role == "assistant"))
        )

    return protocol.Conversation(messages=conv_messages)


def prepare_tree(tree: list[Post], tree_id: UUID) -> protocol.MessageTree:
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
