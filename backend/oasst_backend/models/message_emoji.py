from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel


class MessageEmoji(SQLModel, table=True):
    __tablename__ = "message_emoji"
    __table_args__ = (Index("ix_message_emoji__user_id__message_id", "user_id", "message_id", unique=False),)

    message_id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), sa.ForeignKey("message.id", ondelete="CASCADE"), nullable=False, primary_key=True
        )
    )
    user_id: UUID = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, primary_key=True
        )
    )
    emoji: str = Field(nullable=False, max_length=128, primary_key=True)
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )
