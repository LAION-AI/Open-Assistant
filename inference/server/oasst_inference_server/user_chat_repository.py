import fastapi
import pydantic
import sqlalchemy.orm
import sqlmodel
from loguru import logger
from oasst_inference_server import database, models
from oasst_inference_server.settings import settings
from oasst_shared.schemas import inference


class UserChatRepository(pydantic.BaseModel):
    session: database.AsyncSession
    user_id: str = pydantic.Field(..., min_length=1)

    class Config:
        arbitrary_types_allowed = True

    async def get_chats(
        self,
        include_hidden: bool = False,
        limit: int | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> list[models.DbChat]:
        if after is not None and before is not None:
            raise fastapi.HTTPException(status_code=400, detail="Cannot specify both after and before.")

        query = sqlmodel.select(models.DbChat)
        query = query.where(models.DbChat.user_id == self.user_id)

        if not include_hidden:
            query = query.where(models.DbChat.hidden.is_(False))
        if limit is not None:
            query = query.limit(limit)
        if before is not None:
            query = query.where(models.DbChat.id > before)
        if after is not None:
            query = query.where(models.DbChat.id < after)

        query = query.order_by(models.DbChat.created_at.desc() if before is None else models.DbChat.created_at)

        return (await self.session.exec(query)).all()

    async def get_chat_by_id(self, chat_id: str, include_messages: bool = True) -> models.DbChat:
        query = sqlmodel.select(models.DbChat).where(
            models.DbChat.id == chat_id,
            models.DbChat.user_id == self.user_id,
        )
        if include_messages:
            query = query.options(
                sqlalchemy.orm.selectinload(models.DbChat.messages).selectinload(models.DbMessage.reports),
            )

        chat = (await self.session.exec(query)).one()
        return chat

    async def get_message_by_id(self, chat_id: str, message_id: str) -> models.DbMessage:
        query = (
            sqlmodel.select(models.DbMessage)
            .where(
                models.DbMessage.id == message_id,
                models.DbMessage.chat_id == chat_id,
            )
            .options(
                sqlalchemy.orm.selectinload(models.DbMessage.reports),
            )
            .join(models.DbChat)
            .where(
                models.DbChat.user_id == self.user_id,
            )
        )
        message = (await self.session.exec(query)).one()
        return message

    async def create_chat(self) -> models.DbChat:
        # Try to find the user first
        user: models.DbUser = (
            await self.session.execute(sqlmodel.select(models.DbUser).where(models.DbUser.id == self.user_id))
        ).one_or_none()
        if not user:
            raise fastapi.HTTPException(status_code=404, detail="User not found")
        chat = models.DbChat(user_id=self.user_id)
        self.session.add(chat)
        await self.session.commit()
        return chat

    async def delete_chat(self, chat_id: str) -> models.DbChat:
        chat = await self.get_chat_by_id(chat_id)
        if chat is None:
            raise fastapi.HTTPException(status_code=403)
        logger.debug(f"Deleting {chat_id=}")
        # delete messages
        await self.session.exec(sqlmodel.delete(models.DbMessage).where(models.DbMessage.chat_id == chat_id))
        # delete chat
        await self.session.exec(
            sqlmodel.delete(models.DbChat).where(
                models.DbChat.id == chat_id,
                models.DbChat.user_id == self.user_id,
            )
        )
        await self.session.commit()

    async def add_prompter_message(self, chat_id: str, parent_id: str | None, content: str) -> models.DbMessage:
        logger.info(f"Adding prompter message {len(content)=} to chat {chat_id}")

        if settings.message_max_length is not None:
            if len(content) > settings.message_max_length:
                raise fastapi.HTTPException(status_code=413, detail="Message content exceeds max length")

        chat: models.DbChat = (
            await self.session.exec(
                sqlmodel.select(models.DbChat)
                .options(sqlalchemy.orm.selectinload(models.DbChat.messages))
                .where(
                    models.DbChat.id == chat_id,
                    models.DbChat.user_id == self.user_id,
                )
            )
        ).one()
        if settings.chat_max_messages is not None:
            if len(chat.messages) >= settings.chat_max_messages:
                raise fastapi.HTTPException(status_code=413, detail="Maximum number of messages reached for this chat")
        if parent_id is None:
            if len(chat.messages) > 0:
                raise fastapi.HTTPException(status_code=400, detail="Trying to add first message to non-empty chat")
            if chat.title is None:
                chat.title = content
        else:
            msg_dict = chat.get_msg_dict()
            if parent_id not in msg_dict:
                raise fastapi.HTTPException(status_code=400, detail="Parent message not found")
            if msg_dict[parent_id].role != "assistant":
                raise fastapi.HTTPException(status_code=400, detail="Parent message is not an assistant message")
            if msg_dict[parent_id].state != inference.MessageState.complete:
                raise fastapi.HTTPException(status_code=400, detail="Parent message is not complete")

        message = models.DbMessage(
            role="prompter",
            chat_id=chat_id,
            chat=chat,
            parent_id=parent_id,
            content=content,
        )
        self.session.add(message)
        chat.modified_at = message.created_at

        await self.session.commit()
        logger.debug(f"Added prompter message {len(content)=} to chat {chat_id}")
        query = (
            sqlmodel.select(models.DbMessage)
            .options(
                sqlalchemy.orm.selectinload(models.DbMessage.chat)
                .selectinload(models.DbChat.messages)
                .selectinload(models.DbMessage.reports),
            )
            .where(
                models.DbMessage.id == message.id,
            )
        )
        message = (await self.session.exec(query)).one()
        return message

    async def initiate_assistant_message(
        self, parent_id: str, work_parameters: inference.WorkParameters, worker_compat_hash: str
    ) -> models.DbMessage:
        logger.info(f"Adding stub assistant message to {parent_id=}")

        # find and cancel all pending messages by this user
        pending_msg_query = (
            sqlmodel.select(models.DbMessage)
            .where(
                models.DbMessage.role == "assistant",
                models.DbMessage.state == inference.MessageState.pending,
            )
            .join(models.DbChat)
            .where(
                models.DbChat.user_id == self.user_id,
            )
        )

        pending_msgs: list[models.DbMessage] = (await self.session.exec(pending_msg_query)).all()
        for pending_msg in pending_msgs:
            logger.warning(
                f"User {self.user_id} has a pending message {pending_msg.id} in chat {pending_msg.chat_id}. Cancelling..."
            )
            pending_msg.state = inference.MessageState.cancelled
            await self.session.commit()
            logger.debug(f"Cancelled message {pending_msg.id} in chat {pending_msg.chat_id}.")

        query = (
            sqlmodel.select(models.DbMessage)
            .options(sqlalchemy.orm.selectinload(models.DbMessage.chat))
            .where(
                models.DbMessage.id == parent_id,
                models.DbMessage.role == "prompter",
            )
        )
        parent: models.DbMessage = (await self.session.exec(query)).one()
        if parent.chat.user_id != self.user_id:
            raise fastapi.HTTPException(status_code=400, detail="Message not found")

        if settings.chat_max_messages is not None:
            count_query = sqlmodel.select(sqlmodel.func.count(models.DbMessage.id)).where(
                models.DbMessage.chat_id == parent.chat.id
            )
            num_msgs: int = (await self.session.exec(count_query)).one()

            if num_msgs >= settings.chat_max_messages:
                raise fastapi.HTTPException(status_code=413, detail="Maximum number of messages reached for this chat")

        message = models.DbMessage(
            role="assistant",
            chat_id=parent.chat_id,
            chat=parent.chat,
            parent_id=parent_id,
            state=inference.MessageState.pending,
            work_parameters=work_parameters,
            worker_compat_hash=worker_compat_hash,
        )
        self.session.add(message)
        await self.session.commit()
        logger.debug(f"Initiated assistant message of {parent_id=}")
        query = (
            sqlmodel.select(models.DbMessage)
            .options(
                sqlalchemy.orm.selectinload(models.DbMessage.chat)
                .selectinload(models.DbChat.messages)
                .selectinload(models.DbMessage.reports),
            )
            .where(models.DbMessage.id == message.id)
        )
        message = (await self.session.exec(query)).one()
        return message

    async def update_score(self, message_id: str, score: int) -> models.DbMessage:
        if score < -1 or score > 1:
            raise fastapi.HTTPException(status_code=400, detail="Invalid score")

        logger.info(f"Updating message score to {message_id=}: {score=}")
        query = (
            sqlmodel.select(models.DbMessage)
            .options(sqlalchemy.orm.selectinload(models.DbMessage.chat))
            .where(
                models.DbMessage.id == message_id,
                models.DbMessage.role == "assistant",
            )
        )
        message: models.DbMessage = (await self.session.exec(query)).one()
        if message.chat.user_id != self.user_id:
            raise fastapi.HTTPException(status_code=400, detail="Message not found")
        message.score = score
        await self.session.commit()
        return message

    async def add_report(self, message_id: str, reason: str, report_type: inference.ReportType) -> models.DbReport:
        logger.info(f"Adding report to {message_id=}: {reason=}")
        query = (
            sqlmodel.select(models.DbMessage)
            .options(sqlalchemy.orm.selectinload(models.DbMessage.chat))
            .where(
                models.DbMessage.id == message_id,
                models.DbMessage.role == "assistant",
            )
        )
        message: models.DbMessage = (await self.session.exec(query)).one()
        if message.chat.user_id != self.user_id:
            raise fastapi.HTTPException(status_code=400, detail="Message not found")
        report = models.DbReport(message_id=message.id, reason=reason, report_type=report_type)
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def update_chat(
        self,
        chat_id: str,
        title: str | None = None,
        hidden: bool | None = None,
        allow_data_use: bool | None = None,
    ) -> None:
        logger.info(f"Updating chat {chat_id=}: {title=} {hidden=}")
        chat = await self.get_chat_by_id(chat_id=chat_id, include_messages=False)

        if title is not None:
            logger.info(f"Updating title of chat {chat_id=}: {title=}")
            chat.title = title

        if hidden is not None:
            logger.info(f"Setting chat {chat_id=} to {'hidden' if hidden else 'visible'}")
            chat.hidden = hidden

        if allow_data_use is not None:
            logger.info(f"Updating allow_data_use of chat {chat_id=}: {allow_data_use=}")
            chat.allow_data_use = allow_data_use

        await self.session.commit()
