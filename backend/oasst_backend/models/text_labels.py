from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, SQLModel


class TextLabels(SQLModel, table=True):
    __tablename__ = "text_labels"

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    user_id: UUID = Field(sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False))
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp(), index=True
        ),
    )
    api_client_id: UUID = Field(nullable=False, foreign_key="api_client.id")
    text: str = Field(nullable=False, max_length=2**16)
    message_id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("message.id"), nullable=True, index=True)
    )
    labels: dict[str, float] = Field(default={}, sa_column=sa.Column(pg.JSONB), nullable=False)
    task_id: Optional[UUID] = Field(nullable=True, index=True)
