import fastapi
import sqlmodel
from loguru import logger
from oasst_inference_server import interface, models
from oasst_shared.schemas import protocol
from sqlalchemy.sql.operators import is_not


class ChatRepository:
    def __init__(self, session: sqlmodel.Session) -> None:
        self.session = session

    def get_chats(self) -> list[models.DbChatEntry]:
        return self.session.exec(sqlmodel.select(models.DbChatEntry)).all()

    def get_pending_chats(self) -> list[models.DbChatEntry]:
        return self.session.exec(
            sqlmodel.select(models.DbChatEntry).where(
                is_not(models.DbChatEntry.pending_message_request, None),
                models.DbChatEntry.message_request_state == interface.MessageRequestState.pending,
            )
        ).all()

    def get_chat_list(self) -> list[interface.ChatListEntry]:
        chats = self.get_chats()
        return [chat.to_list_entry() for chat in chats]

    def get_chat_by_id(self, id: str) -> models.DbChatEntry:
        chat = self.session.exec(sqlmodel.select(models.DbChatEntry).where(models.DbChatEntry.id == id)).one()
        return chat

    def get_chat_entry_by_id(self, id: str) -> interface.ChatEntry:
        return self.get_chat_by_id(id).to_entry()

    def create_chat(self) -> models.DbChatEntry:
        chat = models.DbChatEntry()
        self.session.add(chat)
        self.session.commit()
        return chat

    def add_prompter_message(self, id: str, message_request: interface.MessageRequest) -> None:
        logger.info(f"Adding prompter message {message_request} to chat {id}")
        chat = self.get_chat_by_id(id)
        if not chat.conversation.is_prompter_turn:
            raise fastapi.HTTPException(status_code=400, detail="Not your turn")
        if chat.pending_message_request is not None:
            raise fastapi.HTTPException(status_code=400, detail="Already pending")

        chat.conversation.messages.append(
            protocol.ConversationMessage(
                text=message_request.message,
                is_assistant=False,
            )
        )

        chat.pending_message_request = message_request
        chat.message_request_state = interface.MessageRequestState.pending
        self.session.commit()
        logger.debug(f"Added prompter message {message_request} to chat {id}")

    def add_assistant_message(self, id: str, text: str) -> None:
        logger.info(f"Adding assistant message {text} to chat {id}")
        chat = self.get_chat_by_id(id)
        chat.conversation.messages.append(
            protocol.ConversationMessage(
                text=text,
                is_assistant=True,
            )
        )
        chat.pending_message_request = None
        self.session.commit()
        logger.debug(f"Added assistant message {text} to chat {id}")

    def set_chat_state(self, id: str, state: interface.MessageRequestState) -> None:
        logger.info(f"Setting chat {id} state to {state}")
        chat = self.get_chat_by_id(id)
        chat.message_request_state = state
        self.session.commit()
        logger.debug(f"Set chat {id} state to {state}")
