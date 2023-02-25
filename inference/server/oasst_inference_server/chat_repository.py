import datetime

import fastapi
import sqlmodel
from loguru import logger
from oasst_inference_server import database, models
from oasst_shared.schemas import inference


class ChatRepository:
    def __init__(self, session: database.AsyncSession, do_commit=True) -> None:
        self.session = session
        self.do_commit = do_commit

    def as_no_commit(self) -> "ChatRepository":
        return ChatRepository(self.session, do_commit=False)

    async def maybe_commit(self) -> None:
        if self.do_commit:
            await self.session.commit()

    async def get_message_by_role_and_id(self, role: str, message_id: str, for_update=False) -> models.DbMessage:
        query = sqlmodel.select(models.DbMessage).where(
            models.DbMessage.id == message_id, models.DbMessage.role == role
        )
        if for_update:
            query = query.with_for_update()
        message = (await self.session.exec(query)).one()
        return message

    async def get_prompter_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        message = await self.get_message_by_role_and_id("prompter", message_id, for_update=for_update)
        return message

    async def get_assistant_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        message = await self.get_message_by_role_and_id("assistant", message_id, for_update=for_update)
        return message

    async def start_work(
        self, *, message_id: str, worker_id: str, worker_config: inference.WorkerConfig
    ) -> models.DbMessage:
        logger.info(f"Starting work on message {message_id}")
        message = await self.get_assistant_message_by_id(message_id, for_update=True)

        if message.state != inference.MessageState.pending:
            raise fastapi.HTTPException(status_code=400, detail="Message is not pending")

        message.state = inference.MessageState.in_progress
        message.work_begin_at = datetime.datetime.utcnow()
        message.worker_id = worker_id
        message.worker_compat_hash = worker_config.compat_hash
        message.worker_config = worker_config
        await self.maybe_commit()
        logger.debug(f"Started work on message {message_id}")
        await self.session.refresh(message)
        return message

    async def reset_work(self, message_id: str) -> models.DbMessage:
        logger.info(f"Resetting work on message {message_id}")
        message = await self.get_assistant_message_by_id(message_id, for_update=True)
        message.state = inference.MessageState.pending
        message.work_begin_at = None
        message.worker_id = None
        message.worker_compat_hash = None
        message.worker_config = None
        await self.maybe_commit()
        logger.debug(f"Reset work on message {message_id}")
        await self.session.refresh(message)
        return message

    async def abort_work(self, message_id: str, reason: str) -> models.DbMessage:
        logger.info(f"Aborting work on message {message_id}")
        message = self.get_assistant_message_by_id(message_id, for_update=True)
        message.state = inference.MessageState.aborted_by_worker
        message.work_end_at = datetime.datetime.utcnow()
        message.error = reason
        await self.maybe_commit()
        logger.debug(f"Aborted work on message {message_id}")
        await self.session.refresh(message)
        return message

    async def complete_work(self, message_id: str, content: str) -> models.DbMessage:
        logger.info(f"Completing work on message {message_id}")
        message = self.get_assistant_message_by_id(message_id, for_update=True)
        message.state = inference.MessageState.complete
        message.work_end_at = datetime.datetime.utcnow()
        message.content = content
        await self.maybe_commit()
        logger.debug(f"Completed work on message {message_id}")
        await self.session.refresh(message)
        return message
