import datetime
from typing import Annotated, Literal, Union

import pydantic
from oasst_shared.schemas import inference


class CreatePrompterMessageRequest(pydantic.BaseModel):
    parent_id: str | None = None
    content: str = pydantic.Field(..., repr=False)


class CreateAssistantMessageRequest(pydantic.BaseModel):
    parent_id: str
    model_config_name: str
    sampling_parameters: inference.SamplingParameters = pydantic.Field(default_factory=inference.SamplingParameters)
    plugins: list[inference.PluginEntry] = pydantic.Field(default_factory=list[inference.PluginEntry])
    used_plugin: inference.PluginUsed | None = None


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
    message: inference.MessageRead | None = None


class MessageResponseEvent(pydantic.BaseModel):
    event_type: Literal["message"] = "message"
    message: inference.MessageRead


class SafePromptResponseEvent(pydantic.BaseModel):
    event_type: Literal["safe_prompt"] = "safe_prompt"
    safe_prompt: str
    message: inference.MessageRead


ResponseEvent = Annotated[
    Union[TokenResponseEvent, ErrorResponseEvent, MessageResponseEvent, SafePromptResponseEvent],
    pydantic.Field(discriminator="event_type"),
]


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
    hidden: bool = False


class ChatRead(ChatListRead):
    messages: list[inference.MessageRead]


class ListChatsResponse(pydantic.BaseModel):
    chats: list[ChatListRead]
    next: str | None = None
    prev: str | None = None


class MessageCancelledException(Exception):
    def __init__(self, message_id: str):
        super().__init__(f"Message {message_id} was cancelled")
        self.message_id = message_id


class MessageTimeoutException(Exception):
    def __init__(self, message: inference.MessageRead):
        super().__init__(f"Message {message.id} timed out")
        self.message = message


class ChatUpdateRequest(pydantic.BaseModel):
    title: pydantic.constr(max_length=100) | None = None
    hidden: bool | None = None
    allow_data_use: bool | None = None
