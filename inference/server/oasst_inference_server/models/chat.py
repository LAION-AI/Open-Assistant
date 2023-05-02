import datetime

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from oasst_inference_server.schemas import chat as chat_schema
from oasst_shared.schemas import inference
from sqlmodel import Field, Relationship, SQLModel
from uuid_extensions import uuid7str


class DbMessage(SQLModel, table=True):
    __tablename__ = "message"

    role: str = Field(index=True)
    id: str = Field(default_factory=uuid7str, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    chat_id: str = Field(foreign_key="chat.id", index=True)
    chat: "DbChat" = Relationship(back_populates="messages")
    reports: list["DbReport"] = Relationship(back_populates="message")

    parent_id: str | None = Field(None)

    content: str | None = Field(None)
    error: str | None = Field(None)

    safe_content: str | None = Field(None)
    safety_level: int | None = Field(None)
    safety_label: str | None = Field(None)
    safety_rots: str | None = Field(None)

    used_plugin: inference.PluginUsed | None = Field(None, sa_column=sa.Column(pg.JSONB))

    state: inference.MessageState = Field(inference.MessageState.manual)
    work_parameters: inference.WorkParameters = Field(None, sa_column=sa.Column(pg.JSONB))
    work_begin_at: datetime.datetime | None = Field(None)
    work_end_at: datetime.datetime | None = Field(None)
    worker_id: str | None = Field(None, foreign_key="worker.id")
    worker_compat_hash: str | None = Field(None, index=True)
    worker_config: inference.WorkerConfig | None = Field(None, sa_column=sa.Column(pg.JSONB))

    score: int = Field(0)

    @property
    def has_finished(self) -> bool:
        return self.state in (
            inference.MessageState.manual,
            inference.MessageState.complete,
            inference.MessageState.aborted_by_worker,
        )

    @property
    def has_started(self) -> bool:
        if self.has_finished:
            return True
        return self.state in (inference.MessageState.in_progress,)

    def to_read(self) -> inference.MessageRead:
        return inference.MessageRead(
            id=self.id,
            parent_id=self.parent_id,
            chat_id=self.chat_id,
            content=self.content,
            created_at=self.created_at,
            role=self.role,
            state=self.state,
            score=self.score,
            work_parameters=self.work_parameters,
            reports=[r.to_read() for r in self.reports],
            safe_content=self.safe_content,
            safety_level=self.safety_level,
            safety_label=self.safety_label,
            safety_rots=self.safety_rots,
            used_plugin=self.used_plugin,
        )


class DbChat(SQLModel, table=True):
    __tablename__ = "chat"

    id: str = Field(default_factory=uuid7str, primary_key=True)

    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, index=True)
    modified_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, index=True)
    title: str | None = Field(None)

    messages: list[DbMessage] = Relationship(back_populates="chat")

    hidden: bool = Field(False, sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.false()))

    allow_data_use: bool = Field(True, sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.true()))

    def to_list_read(self) -> chat_schema.ChatListRead:
        return chat_schema.ChatListRead(
            id=self.id,
            created_at=self.created_at,
            modified_at=self.modified_at,
            title=self.title,
            hidden=self.hidden,
        )

    def to_read(self) -> chat_schema.ChatRead:
        return chat_schema.ChatRead(
            id=self.id,
            created_at=self.created_at,
            modified_at=self.modified_at,
            title=self.title,
            messages=[m.to_read() for m in self.messages],
            hidden=self.hidden,
        )

    def get_msg_dict(self) -> dict[str, DbMessage]:
        return {m.id: m for m in self.messages}


class DbReport(SQLModel, table=True):
    __tablename__ = "report"

    id: str = Field(default_factory=uuid7str, primary_key=True)
    message_id: str = Field(..., foreign_key="message.id", index=True)
    message: DbMessage = Relationship(back_populates="reports")
    report_type: inference.ReportType = Field(...)
    reason: str = Field(...)

    def to_read(self) -> inference.Report:
        return inference.Report(id=self.id, report_type=self.report_type, reason=self.reason)
