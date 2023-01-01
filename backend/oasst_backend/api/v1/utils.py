# -*- coding: utf-8 -*-

from http import HTTPStatus
from uuid import UUID

from oasst_backend.exceptions import OasstError, OasstErrorCode
from oasst_backend.models import Message
from oasst_backend.models.db_payload import MessagePayload
from oasst_shared.schemas import protocol


def prepare_message(m: Message) -> protocol.Message:
    if not isinstance(m.payload.payload, MessagePayload):
        raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
    return protocol.Message(
        id=m.id,
        parent_id=m.parent_id,
        text=m.payload.payload.text,
        is_assistant=(m.role == "assistant"),
        created_date=m.created_date,
    )


def prepare_message_list(messages: list[Message]) -> list[protocol.Message]:
    return [prepare_message(m) for m in messages]


def prepare_conversation(messages: list[Message]) -> protocol.Conversation:
    conv_messages = []
    for message in messages:
        if not isinstance(message.payload.payload, MessagePayload):
            raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        conv_messages.append(
            protocol.ConversationMessage(text=message.payload.payload.text, is_assistant=(message.role == "assistant"))
        )

    return protocol.Conversation(messages=conv_messages)


def prepare_tree(tree: list[Message], tree_id: UUID) -> protocol.MessageTree:
    tree_messages = []
    for message in tree:
        if not isinstance(message.payload.payload, MessagePayload):
            raise OasstError("Server error", OasstErrorCode.SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        tree_messages.append(prepare_message(message))

    return protocol.MessageTree(id=tree_id, messages=tree_messages)
