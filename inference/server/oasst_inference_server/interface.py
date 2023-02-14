import enum

import pydantic
from oasst_shared.schemas import inference, protocol


class MessageRequest(pydantic.BaseModel):
    message: str = pydantic.Field(..., repr=False)
    model_name: str = "distilgpt2"
    max_new_tokens: int = 100

    @property
    def worker_compat_hash(self) -> str:
        return inference.compat_hash(model_name=self.model_name)


class TokenResponseEvent(pydantic.BaseModel):
    token: inference.TokenResponse


class MessageRequestState(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"
    aborted_by_worker = "aborted_by_worker"


class CreateChatRequest(pydantic.BaseModel):
    pass


class ChatListEntry(pydantic.BaseModel):
    id: str


class ChatEntry(pydantic.BaseModel):
    id: str
    conversation: protocol.Conversation


class ListChatsResponse(pydantic.BaseModel):
    chats: list[ChatListEntry]


class CreateWorkerRequest(pydantic.BaseModel):
    name: str
