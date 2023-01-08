from typing import List
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import ARRAY, Field, Float, SQLModel


class MessageEmbedding(SQLModel, table=True):
    __tablename__ = "message_embedding"
    __table_args__ = (sa.PrimaryKeyConstraint("message_id", "model"),)

    message_id: UUID = Field(sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("message.id"), nullable=False))
    model: str = Field(max_length=256, nullable=False)
    embedding: List[float] = Field(sa_column=sa.Column(ARRAY(Float)), nullable=True)
