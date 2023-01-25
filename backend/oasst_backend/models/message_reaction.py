from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, SQLModel

from .payload_column_type import PayloadContainer, payload_column_type


class MessageReaction(SQLModel, table=True):
    __tablename__ = "message_reaction"

    task_id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("task.id"), nullable=False, primary_key=True)
    )
    user_id: UUID = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False, primary_key=True)
    )
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp(), index=True
        )
    )
    payload_type: str = Field(nullable=False, max_length=200)
    payload: PayloadContainer = Field(sa_column=sa.Column(payload_column_type(PayloadContainer), nullable=False))
    api_client_id: UUID = Field(nullable=False, foreign_key="api_client.id")
    message_id: Optional[UUID] = Field(nullable=True, index=True)
