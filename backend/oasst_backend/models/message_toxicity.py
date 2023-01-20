from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Float, SQLModel


class MessageToxicity(SQLModel, table=True):
    __tablename__ = "message_toxicity"
    __table_args__ = (sa.PrimaryKeyConstraint("message_id", "model"),)

    message_id: UUID = Field(sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("message.id"), nullable=False))
    model: str = Field(max_length=256, nullable=False)

    # Storing the score and the label of the message
    score: float = Field(sa_column=sa.Column(Float), nullable=False)
    label: str = Field(max_length=256, nullable=False)

    # In the case that the Message Embedding is created afterwards
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )
