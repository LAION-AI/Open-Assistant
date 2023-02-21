import datetime
from uuid import uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from oasst_inference_server import interface
from oasst_shared.schemas import inference
from sqlmodel import Field, Relationship, SQLModel


class DbMessage(SQLModel, table=True):
    __tablename__ = "message"

    role: str = Field(..., index=True)
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    chat_id: str = Field(..., foreign_key="chat.id", index=True)
    chat: "DbChat" = Relationship(back_populates="messages")

    parent_id: str | None = Field(None)

    content: str | None = Field(None)
    error: str | None = Field(None)

    state: inference.MessageState = Field(inference.MessageState.manual)
    work_parameters: inference.WorkParameters = Field(None, sa_column=sa.Column(pg.JSONB))
    work_begin_at: datetime.datetime | None = Field(None)
    work_end_at: datetime.datetime | None = Field(None)
    worker_id: str | None = Field(None, foreign_key="worker.id")
    worker_compat_hash: str | None = Field(None, index=True)
    worker_config: inference.WorkerConfig | None = Field(None, sa_column=sa.Column(pg.JSONB))

    def to_read(self) -> inference.MessageRead:
        return inference.MessageRead(
            id=self.id,
            content=self.content,
            role=self.role,
            state=self.state,
        )


class DbChat(SQLModel, table=True):
    __tablename__ = "chat"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    messages: list[DbMessage] = Relationship(back_populates="chat")

    def to_list_read(self) -> interface.ChatListRead:
        return interface.ChatListRead(id=self.id)

    def to_read(self) -> interface.ChatRead:
        return interface.ChatRead(id=self.id, messages=[m.to_read() for m in self.messages])

    def get_msg_dict(self) -> dict[str, DbMessage]:
        return {m.id: m for m in self.messages}


class DbWorker(SQLModel, table=True):
    __tablename__ = "worker"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    api_key: str = Field(default_factory=lambda: str(uuid4()), index=True)
    name: str

    in_compliance_check: bool = Field(default=False, sa_column=sa.Column(sa.Boolean, server_default=sa.text("false")))
    next_compliance_check: datetime.datetime | None = Field(None)
