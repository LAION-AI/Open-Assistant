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
    system_prompt: str | None = None
    user_profile: str | None = None
    user_response_instructions: str | None = None
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


class PluginIntermediateResponseEvent(pydantic.BaseModel):
    event_type: Literal["plugin_intermediate"] = "plugin_intermediate"
    current_plugin_thought: str
    current_plugin_action_taken: str
    current_plugin_action_input: str
    current_plugin_action_response: str
    message: inference.MessageRead | None = None


ResponseEvent = Annotated[
    Union[
        TokenResponseEvent,
        ErrorResponseEvent,
        MessageResponseEvent,
        SafePromptResponseEvent,
        PluginIntermediateResponseEvent,
    ],
    pydantic.Field(discriminator="event_type"),
]


class VoteRequest(pydantic.BaseModel):
    score: int


class MessageEvalRequest(pydantic.BaseModel):
    inferior_message_ids: list[str]


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
    allow_data_use: bool = True
    active_thread_tail_message_id: str | None


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
    active_thread_tail_message_id: str | None = None
