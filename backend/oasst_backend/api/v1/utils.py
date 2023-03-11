import re
from uuid import UUID

from oasst_backend.models import Message
from oasst_shared.schemas import protocol


def prepare_message(m: Message) -> protocol.Message:
    return protocol.Message(
        id=m.id,
        frontend_message_id=m.frontend_message_id,
        parent_id=m.parent_id,
        user_id=m.user_id,
        text=m.text,
        lang=m.lang,
        is_assistant=(m.role == "assistant"),
        created_date=m.created_date,
        emojis=m.emojis or {},
        user_emojis=m.user_emojis or [],
        user_is_author=m.user_is_author,
        review_result=m.review_result,
        review_count=m.review_count,
        ranking_count=m.ranking_count,
        deleted=m.deleted,
        synthetic=m.synthetic,
        model_name=m.model_name,
        message_tree_id=m.message_tree_id,
        rank=m.rank,
        user=m.user.to_protocol_frontend_user() if m.user else None,
    )


def prepare_message_list(messages: list[Message]) -> list[protocol.Message]:
    return [prepare_message(m) for m in messages]


def prepare_conversation_message(message: Message) -> protocol.ConversationMessage:
    return protocol.ConversationMessage(
        id=message.id,
        user_id=message.user_id,
        frontend_message_id=message.frontend_message_id,
        text=message.text,
        lang=message.lang,
        is_assistant=(message.role == "assistant"),
        emojis=message.emojis or {},
        user_emojis=message.user_emojis or [],
        user_is_author=message.user_is_author,
        synthetic=message.synthetic,
    )


def prepare_conversation_message_list(messages: list[Message]) -> list[protocol.ConversationMessage]:
    return [prepare_conversation_message(message) for message in messages]


def prepare_conversation(messages: list[Message]) -> protocol.Conversation:
    return protocol.Conversation(messages=prepare_conversation_message_list(messages))


def prepare_tree(tree: list[Message], tree_id: UUID) -> protocol.MessageTree:
    tree_messages = []
    for message in tree:
        tree_messages.append(prepare_message(message))

    return protocol.MessageTree(id=tree_id, messages=tree_messages)


split_uuid_pattern = re.compile(
    r"^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\$(.*)$"
)
