from uuid import UUID

from oasst_backend.models import Message
from oasst_shared.schemas import protocol


def prepare_message(m: Message) -> protocol.Message:
    return protocol.Message(
        id=m.id,
        parent_id=m.parent_id,
        text=m.text,
        is_assistant=(m.role == "assistant"),
        created_date=m.created_date,
    )


def prepare_message_list(messages: list[Message]) -> list[protocol.Message]:
    return [prepare_message(m) for m in messages]


def prepare_conversation(messages: list[Message]) -> protocol.Conversation:
    conv_messages = []
    for message in messages:
        conv_messages.append(
            protocol.ConversationMessage(
                text=message.text,
                is_assistant=(message.role == "assistant"),
                message_id=message.id,
                frontend_message_id=message.frontend_message_id,
            )
        )

    return protocol.Conversation(messages=conv_messages)


def prepare_tree(tree: list[Message], tree_id: UUID) -> protocol.MessageTree:
    tree_messages = []
    for message in tree:
        tree_messages.append(prepare_message(message))

    return protocol.MessageTree(id=tree_id, messages=tree_messages)
