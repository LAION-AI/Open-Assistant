import fastapi
import sqlmodel
from loguru import logger
from oasst_inference_server import interface, models
from oasst_shared.schemas import protocol
from sqlalchemy.sql.operators import is_not


class ChatRepository:
    def __init__(self, session: sqlmodel.Session, do_commit=True) -> None:
        self.session = session
        self.do_commit = do_commit

    def as_no_commit(self) -> "ChatRepository":
        return ChatRepository(self.session, do_commit=False)

    def maybe_commit(self) -> None:
        if self.do_commit:
            self.session.commit()

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

    def get_chat_by_id(self, chat_id: str, for_update=False) -> models.DbChatEntry:
        query = sqlmodel.select(models.DbChatEntry).where(models.DbChatEntry.id == chat_id)
        if for_update:
            query = query.with_for_update()
        chat = self.session.exec(query).one()
        return chat

    def get_chat_entry_by_id(self, chat_id: str) -> interface.ChatEntry:
        return self.get_chat_by_id(chat_id).to_entry()

    def create_chat(self) -> models.DbChatEntry:
        chat = models.DbChatEntry()
        self.session.add(chat)
        self.maybe_commit()
        return chat

    def add_prompter_message(self, chat_id: str, message_request: interface.MessageRequest) -> None:
        logger.info(f"Adding prompter message {message_request} to chat {chat_id}")
        chat = self.get_chat_by_id(chat_id, for_update=True)
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
        self.maybe_commit()
        logger.debug(f"Added prompter message {message_request} to chat {chat_id}")

    def add_assistant_message(self, chat_id: str, text: str) -> None:
        logger.info(f"Adding assistant message {text} to chat {chat_id}")
        chat = self.get_chat_by_id(chat_id, for_update=True)
        chat.conversation.messages.append(
            protocol.ConversationMessage(
                text=text,
                is_assistant=True,
            )
        )
        chat.pending_message_request = None
        self.maybe_commit()
        logger.debug(f"Added assistant message {text} to chat {chat_id}")

    def set_chat_state(self, chat_id: str, state: interface.MessageRequestState) -> None:
        logger.info(f"Setting chat {chat_id} state to {state}")
        chat = self.get_chat_by_id(chat_id, for_update=True)
        chat.message_request_state = state
        self.maybe_commit()
        logger.debug(f"Set chat {chat_id} state to {state}")
