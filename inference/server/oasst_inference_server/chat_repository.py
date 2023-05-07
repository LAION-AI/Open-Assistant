import datetime

import fastapi
import pydantic
import sqlalchemy.orm
import sqlmodel
from loguru import logger
from oasst_inference_server import database, models
from oasst_inference_server.schemas import chat as chat_schema
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference


class ChatRepository(pydantic.BaseModel):
    session: database.AsyncSession

    class Config:
        arbitrary_types_allowed = True

    async def get_assistant_message_by_id(self, message_id: str) -> models.DbMessage:
        query = (
            sqlmodel.select(models.DbMessage)
            .options(sqlalchemy.orm.selectinload(models.DbMessage.reports))
            .where(models.DbMessage.id == message_id, models.DbMessage.role == "assistant")
        )
        message = (await self.session.exec(query)).one()
        return message

    async def get_prompter_message_by_id(self, message_id: str) -> models.DbMessage:
        query = (
            sqlmodel.select(models.DbMessage)
            .options(sqlalchemy.orm.selectinload(models.DbMessage.reports))
            .where(models.DbMessage.id == message_id, models.DbMessage.role == "prompter")
        )
        message = (await self.session.exec(query)).one()
        return message

    async def start_work(
        self, *, message_id: str, worker_id: str, worker_config: inference.WorkerConfig
    ) -> models.DbMessage:
        logger.debug(f"Starting work on message {message_id}")
        message = await self.get_assistant_message_by_id(message_id)

        if settings.assistant_message_timeout > 0:
            message_age_in_seconds = (datetime.datetime.utcnow() - message.created_at).total_seconds()
            if message_age_in_seconds > settings.assistant_message_timeout:
                message.state = inference.MessageState.timeout
                await self.session.commit()
                await self.session.refresh(message)
                raise chat_schema.MessageTimeoutException(message=message.to_read())

        if message.state == inference.MessageState.cancelled:
            raise chat_schema.MessageCancelledException(message_id=message_id)

        if message.state != inference.MessageState.pending:
            raise fastapi.HTTPException(status_code=400, detail="Message is not pending")

        message.state = inference.MessageState.in_progress
        message.work_begin_at = datetime.datetime.utcnow()
        message.worker_id = worker_id
        message.worker_config = worker_config
        await self.session.commit()
        logger.debug(f"Started work on message {message_id}")
        await self.session.refresh(message)
        return message

    async def reset_work(self, message_id: str) -> models.DbMessage:
        logger.warning(f"Resetting work on message {message_id}")
        message = await self.get_assistant_message_by_id(message_id)
        message.state = inference.MessageState.pending
        message.work_begin_at = None
        message.worker_id = None
        message.worker_compat_hash = None
        message.worker_config = None
        await self.session.commit()
        logger.debug(f"Reset work on message {message_id}")
        await self.session.refresh(message)
        return message

    async def abort_work(self, message_id: str, reason: str) -> models.DbMessage:
        logger.warning(f"Aborting work on message {message_id}")
        message = await self.get_assistant_message_by_id(message_id)
        message.state = inference.MessageState.aborted_by_worker
        message.work_end_at = datetime.datetime.utcnow()
        message.error = reason
        await self.session.commit()
        logger.debug(f"Aborted work on message {message_id}")
        await self.session.refresh(message)
        return message

    async def complete_work(self, message_id: str, content: str, used_plugin: inference.PluginUsed) -> models.DbMessage:
        logger.debug(f"Completing work on message {message_id}")
        message = await self.get_assistant_message_by_id(message_id)
        message.state = inference.MessageState.complete
        message.work_end_at = datetime.datetime.utcnow()
        message.content = content
        message.used_plugin = used_plugin
        await self.session.commit()
        logger.debug(f"Completed work on message {message_id}")
        await self.session.refresh(message)
        return message
