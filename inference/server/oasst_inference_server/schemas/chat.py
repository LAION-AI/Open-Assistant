import datetime
from typing import Annotated, Literal, Union

import pydantic
from oasst_shared.schemas import inference


class CreateMessageRequest(pydantic.BaseModel):
    parent_id: str | None = None
    content: str = pydantic.Field(..., repr=False)
    work_parameters: inference.WorkParameters = pydantic.Field(default_factory=inference.WorkParameters)

    @property
    def worker_compat_hash(self) -> str:
        return inference.compat_hash(model_name=self.work_parameters.model_name)


class CreateMessageResponse(pydantic.BaseModel):
    prompter_message: inference.MessageRead
    assistant_message: inference.MessageRead


class PendingResponseEvent(pydantic.BaseModel):
    event_type: Literal["pending"] = "pending"
    queue_position: int
    queue_size: int


class TokenResponseEvent(pydantic.BaseModel):
    event_type: Literal["token"] = "token"
    text: str


class ErrorResponseEvent(pydantic.BaseModel):
    event_type: Literal["error"] = "error"
    error: str


class MessageResponseEvent(pydantic.BaseModel):
    event_type: Literal["message"] = "message"
    message: inference.MessageRead


ResponseEvent = Annotated[Union[TokenResponseEvent, ErrorResponseEvent], pydantic.Field(discriminator="event_type")]


class VoteRequest(pydantic.BaseModel):
    score: int


class ReportRequest(pydantic.BaseModel):
    report_type: inference.ReportType
    reason: str


class CreateChatRequest(pydantic.BaseModel):
    pass


class ChatListRead(pydantic.BaseModel):
    id: str
    created_at: datetime.datetime
    modified_at: datetime.datetime
    title: str | None


class ChatRead(ChatListRead):
    messages: list[inference.MessageRead]


class ListChatsResponse(pydantic.BaseModel):
    chats: list[ChatListRead]
