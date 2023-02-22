import datetime

import fastapi
import sqlmodel
from loguru import logger
from oasst_inference_server import interface, models
from oasst_shared.schemas import inference
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

    def get_chats(self) -> list[models.DbChat]:
        return self.session.exec(sqlmodel.select(models.DbChat)).all()

    def get_pending_chats(self) -> list[models.DbChat]:
        return self.session.exec(
            sqlmodel.select(models.DbChat).where(
                is_not(models.DbChat.pending_message_request, None),
                models.DbChat.message_request_state == interface.MessageRequestState.pending,
            )
        ).all()

    def get_chat_list(self) -> list[interface.ChatListRead]:
        chats = self.get_chats()
        return [chat.to_read() for chat in chats]

    def get_prompter_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        query = sqlmodel.select(models.DbMessage).where(
            models.DbMessage.id == message_id, models.DbMessage.role == "prompter"
        )
        if for_update:
            query = query.with_for_update()
        message = self.session.exec(query).one()
        return message

    def get_assistant_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        query = sqlmodel.select(models.DbMessage).where(
            models.DbMessage.id == message_id, models.DbMessage.role == "assistant"
        )
        if for_update:
            query = query.with_for_update()
        message = self.session.exec(query).one()
        return message

    def get_chat_by_id(self, chat_id: str, for_update=False) -> models.DbChat:
        query = sqlmodel.select(models.DbChat).where(models.DbChat.id == chat_id)
        if for_update:
            query = query.with_for_update()
        chat = self.session.exec(query).one()
        return chat

    def create_chat(self) -> models.DbChat:
        chat = models.DbChat()
        self.session.add(chat)
        self.maybe_commit()
        return chat

    def add_prompter_message(self, chat_id: str, parent_id: str | None, content: str) -> models.DbMessage:
        logger.info(f"Adding prompter message {len(content)=} to chat {chat_id}")
        chat = self.get_chat_by_id(chat_id)
        if parent_id is None:
            if len(chat.messages) > 0:
                raise fastapi.HTTPException(status_code=400, detail="Trying to add first message to non-empty chat")
        else:
            msg_dict = chat.get_msg_dict()
            if parent_id not in msg_dict:
                raise fastapi.HTTPException(status_code=400, detail="Parent message not found")
            if msg_dict[parent_id].role != "assistant":
                raise fastapi.HTTPException(status_code=400, detail="Parent message is not an assistant message")

        message = models.DbMessage(
            role="prompter",
            chat_id=chat_id,
            chat=chat,
            parent_id=parent_id,
            content=content,
        )
        self.session.add(message)

        self.maybe_commit()
        logger.debug(f"Added prompter message {len(content)=} to chat {chat_id}")
        self.session.refresh(message)
        return message

    def initiate_assistant_message(self, parent_id: str, work_parameters: inference.WorkParameters) -> models.DbMessage:
        logger.info(f"Adding stub assistant message to {parent_id=}")
        parent = self.get_prompter_message_by_id(parent_id)
        message = models.DbMessage(
            role="assistant",
            chat_id=parent.chat_id,
            chat=parent.chat,
            parent_id=parent_id,
            state=inference.MessageState.pending,
            work_parameters=work_parameters,
        )
        self.session.add(message)
        self.maybe_commit()
        logger.debug(f"Initiated assistant message of {parent_id=}")
        self.session.refresh(message)
        return message

    def start_work(self, *, message_id: str, worker_id: str, worker_config: inference.WorkerConfig) -> models.DbMessage:
        logger.info(f"Starting work on message {message_id}")
        message = self.get_assistant_message_by_id(message_id, for_update=True)

        if message.state != inference.MessageState.pending:
            raise fastapi.HTTPException(status_code=400, detail="Message is not pending")

        message.state = inference.MessageState.in_progress
        message.work_begin_at = datetime.datetime.utcnow()
        message.worker_id = worker_id
        message.worker_compat_hash = worker_config.compat_hash
        message.worker_config = worker_config
        self.maybe_commit()
        logger.debug(f"Started work on message {message_id}")
        self.session.refresh(message)
        return message

    def reset_work(self, message_id: str) -> models.DbMessage:
        logger.info(f"Resetting work on message {message_id}")
        message = self.get_assistant_message_by_id(message_id, for_update=True)
        message.state = inference.MessageState.pending
        message.work_begin_at = None
        message.worker_id = None
        message.worker_compat_hash = None
        message.worker_config = None
        self.maybe_commit()
        logger.debug(f"Reset work on message {message_id}")
        self.session.refresh(message)
        return message

    def abort_work(self, message_id: str, reason: str) -> models.DbMessage:
        logger.info(f"Aborting work on message {message_id}")
        message = self.get_assistant_message_by_id(message_id, for_update=True)
        message.state = inference.MessageState.aborted_by_worker
        message.work_end_at = datetime.datetime.utcnow()
        message.error = reason
        self.maybe_commit()
        logger.debug(f"Aborted work on message {message_id}")
        self.session.refresh(message)
        return message

    def complete_work(self, message_id: str, content: str) -> models.DbMessage:
        logger.info(f"Completing work on message {message_id}")
        message = self.get_assistant_message_by_id(message_id, for_update=True)
        message.state = inference.MessageState.complete
        message.work_end_at = datetime.datetime.utcnow()
        message.content = content
        self.maybe_commit()
        logger.debug(f"Completed work on message {message_id}")
        self.session.refresh(message)
        return message
