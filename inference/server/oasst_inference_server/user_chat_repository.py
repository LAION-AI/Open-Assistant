import fastapi
import pydantic
import sqlalchemy.orm
import sqlmodel
from loguru import logger
from oasst_inference_server import database, models
from oasst_shared.schemas import inference


class UserChatRepository(pydantic.BaseModel):
    session: database.AsyncSession
    user_id: str = pydantic.Field(..., min_length=1)

    class Config:
        arbitrary_types_allowed = True

    async def get_chats(self) -> list[models.DbChat]:
        query = sqlmodel.select(models.DbChat)
        query = query.where(models.DbChat.user_id == self.user_id)
        return (await self.session.exec(query)).all()

    async def get_chat_by_id(self, chat_id: str) -> models.DbChat:
        query = (
            sqlmodel.select(models.DbChat)
            .options(
                sqlalchemy.orm.selectinload(models.DbChat.messages).selectinload(models.DbMessage.reports),
            )
            .where(
                models.DbChat.id == chat_id,
                models.DbChat.user_id == self.user_id,
            )
        )
        chat = (await self.session.exec(query)).one()
        return chat

    async def create_chat(self) -> models.DbChat:
        chat = models.DbChat(user_id=self.user_id)
        self.session.add(chat)
        await self.session.commit()
        return chat

    async def add_prompter_message(self, chat_id: str, parent_id: str | None, content: str) -> models.DbMessage:
        logger.info(f"Adding prompter message {len(content)=} to chat {chat_id}")
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
        self, parent_id: str, work_parameters: inference.WorkParameters
    ) -> models.DbMessage:
        logger.info(f"Adding stub assistant message to {parent_id=}")
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
        message = models.DbMessage(
            role="assistant",
            chat_id=parent.chat_id,
            chat=parent.chat,
            parent_id=parent_id,
            state=inference.MessageState.pending,
            work_parameters=work_parameters,
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
