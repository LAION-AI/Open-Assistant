from uuid import uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from oasst_inference_server import interface
from oasst_shared.schemas import protocol
from sqlmodel import Field, SQLModel


class DbChatEntry(SQLModel, table=True):
    __tablename__ = "chat"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    conversation: protocol.Conversation = Field(default_factory=protocol.Conversation, sa_column=sa.Column(pg.JSONB))
    pending_message_request: interface.MessageRequest | None = Field(None, sa_column=sa.Column(pg.JSONB))
    message_request_state: interface.MessageRequestState | None = Field(None, sa_column=sa.Column(pg.JSONB))

    def to_list_entry(self) -> interface.ChatListEntry:
        return interface.ChatListEntry(id=self.id)

    def to_entry(self) -> interface.ChatEntry:
        return interface.ChatEntry(id=self.id, conversation=self.conversation)


class DbWorkerEntry(SQLModel, table=True):
    __tablename__ = "worker"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    api_key: str = Field(default_factory=lambda: str(uuid4()), index=True)
    name: str
