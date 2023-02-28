import fastapi
import pydantic
import sqlmodel
from loguru import logger
from oasst_inference_server import models
from oasst_shared.schemas import inference


class UserChatRepository(pydantic.BaseModel):
    session: sqlmodel.Session
    user_id: str = pydantic.Field(..., min_length=1)
    do_commit: bool = True

    class Config:
        arbitrary_types_allowed = True

    def as_no_commit(self) -> "UserChatRepository":
        return UserChatRepository(session=self.session, user_id=self.user_id, do_commit=False)

    def maybe_commit(self) -> None:
        if self.do_commit:
            self.session.commit()

    def get_chats(self) -> list[models.DbChat]:
        query = sqlmodel.select(models.DbChat)
        query = query.where(models.DbChat.user_id == self.user_id)
        return self.session.exec(query).all()

    def get_chat_by_id(self, chat_id: str, for_update=False) -> models.DbChat:
        query = sqlmodel.select(models.DbChat).where(models.DbChat.id == chat_id)
        query = query.where(models.DbChat.user_id == self.user_id)
        if for_update:
            query = query.with_for_update()
        chat = self.session.exec(query).one()
        return chat

    def create_chat(self) -> models.DbChat:
        chat = models.DbChat(user_id=self.user_id)
        self.session.add(chat)
        self.maybe_commit()
        return chat

    def get_prompter_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        query = sqlmodel.select(models.DbMessage).where(
            models.DbMessage.id == message_id,
            models.DbMessage.role == "prompter",
        )
        if for_update:
            query = query.with_for_update()
        message = self.session.exec(query).one()
        if message.chat.user_id != self.user_id:
            raise fastapi.HTTPException(status_code=400, detail="Message not found")
        return message

    def get_assistant_message_by_id(self, message_id: str, for_update=False) -> models.DbMessage:
        query = sqlmodel.select(models.DbMessage).where(
            models.DbMessage.id == message_id,
            models.DbMessage.role == "assistant",
        )
        if for_update:
            query = query.with_for_update()
        message = self.session.exec(query).one()
        if message.chat.user_id != self.user_id:
            raise fastapi.HTTPException(status_code=400, detail="Message not found")
        return message

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

    def add_vote(self, message_id: str, score: int) -> models.DbVote:
        logger.info(f"Adding vote to {message_id=}: {score=}")
        message = self.get_assistant_message_by_id(message_id)
        vote = models.DbVote(
            message_id=message.id,
            score=score,
        )
        self.session.add(vote)
        self.maybe_commit()
        self.session.refresh(vote)
        return vote

    def add_report(self, message_id: str, reason: str, report_type: inference.ReportType) -> models.DbReport:
        logger.info(f"Adding report to {message_id=}: {reason=}")
        message = self.get_assistant_message_by_id(message_id)
        report = models.DbReport(message_id=message.id, reason=reason, report_type=report_type)
        self.session.add(report)
        self.maybe_commit()
        self.session.refresh(report)
        return report
