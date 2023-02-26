import datetime

import fastapi
import sqlmodel
from loguru import logger
from oasst_inference_server import models
from oasst_inference_server.schemas import chat as chat_schema
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
        query = sqlmodel.select(models.DbChat)
        return self.session.exec(query).all()

    def get_pending_chats(self) -> list[models.DbChat]:
        return self.session.exec(
            sqlmodel.select(models.DbChat).where(
                is_not(models.DbChat.pending_message_request, None),
                models.DbChat.message_request_state == chat_schema.MessageRequestState.pending,
            )
        ).all()

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
