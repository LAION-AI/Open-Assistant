import fastapi
import pydantic
import sqlmodel
from loguru import logger
from oasst_inference_server import database, models
from oasst_shared.schemas import inference

# from sqlalchemy import orm


class UserChatRepository(pydantic.BaseModel):
    session: database.AsyncSession
    user_id: str = pydantic.Field(..., min_length=1)
    do_commit: bool = True

    class Config:
        arbitrary_types_allowed = True

    def as_no_commit(self) -> "UserChatRepository":
        return UserChatRepository(session=self.session, user_id=self.user_id, do_commit=False)

    async def maybe_commit(self) -> None:
        if self.do_commit:
            await self.session.commit()

    async def get_chats(self) -> list[models.DbChat]:
        query = sqlmodel.select(models.DbChat)
        query = query.where(models.DbChat.user_id == self.user_id)
        return (await self.session.exec(query)).all()

    async def get_chat_by_id(self, chat_id: str, for_update=False) -> models.DbChat:
        query = sqlmodel.select(models.DbChat)
        # query = query.options(
        # orm.joinedload(models.DbChat.messages)
        # orm.selectinload(models.DbChat.messages)
        # )
        query = query.where(models.DbChat.id == chat_id)
        query = query.where(models.DbChat.user_id == self.user_id)
        if for_update:
            query = query.with_for_update()
        result = await self.session.exec(query)
        # result = result.unique()
        chat = result.one()
        return chat

    async def create_chat(self) -> models.DbChat:
        chat = models.DbChat(user_id=self.user_id)
        self.session.add(chat)
        await self.maybe_commit()
        return chat

    async def get_prompter_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        query = sqlmodel.select(models.DbMessage).where(
            models.DbMessage.id == message_id,
            models.DbMessage.role == "prompter",
        )
        if for_update:
            query = query.with_for_update()
        message = (await self.session.exec(query)).one()
        if message.chat.user_id != self.user_id:
            raise fastapi.HTTPException(status_code=400, detail="Message not found")
        return message

    async def get_assistant_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        query = sqlmodel.select(models.DbMessage).where(
            models.DbMessage.id == message_id,
            models.DbMessage.role == "assistant",
        )
        if for_update:
            query = query.with_for_update()
        message = (await self.session.exec(query)).one()
        if message.chat.user_id != self.user_id:
            raise fastapi.HTTPException(status_code=400, detail="Message not found")
        return message

    async def add_prompter_message(self, chat_id: str, parent_id: str | None, content: str) -> models.DbMessage:
        logger.info(f"Adding prompter message {len(content)=} to chat {chat_id}")
        chat = await self.get_chat_by_id(chat_id)
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

        await self.maybe_commit()
        logger.debug(f"Added prompter message {len(content)=} to chat {chat_id}")
        await self.session.refresh(message)
        return message

    async def initiate_assistant_message(
        self, parent_id: str, work_parameters: inference.WorkParameters
    ) -> models.DbMessage:
        logger.info(f"Adding stub assistant message to {parent_id=}")
        parent = await self.get_prompter_message_by_id(parent_id)
        message = models.DbMessage(
            role="assistant",
            chat_id=parent.chat_id,
            chat=parent.chat,
            parent_id=parent_id,
            state=inference.MessageState.pending,
            work_parameters=work_parameters,
        )
        self.session.add(message)
        await self.maybe_commit()
        logger.debug(f"Initiated assistant message of {parent_id=}")
        await self.session.refresh(message)
        return message

    async def add_vote(self, message_id: str, score: int) -> models.DbVote:
        logger.info(f"Adding vote to {message_id=}: {score=}")
        message = await self.get_assistant_message_by_id(message_id)
        vote = models.DbVote(
            message_id=message.id,
            score=score,
        )
        self.session.add(vote)
        await self.maybe_commit()
        await self.session.refresh(vote)
        return vote

    async def add_report(self, message_id: str, reason: str, report_type: inference.ReportType) -> models.DbReport:
        logger.info(f"Adding report to {message_id=}: {reason=}")
        message = await self.get_assistant_message_by_id(message_id)
        report = models.DbReport(message_id=message.id, reason=reason, report_type=report_type)
        self.session.add(report)
        await self.maybe_commit()
        await self.session.refresh(report)
        return report
