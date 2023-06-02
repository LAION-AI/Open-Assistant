from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, SQLModel

from .payload_column_type import PayloadContainer, payload_column_type


class MessageRevision(SQLModel, table=True):
    __tablename__ = "message_revision"

    id: UUID = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        )
    )

    payload: Optional[PayloadContainer] = Field(
        sa_column=sa.Column(payload_column_type(PayloadContainer), nullable=True)
    )
    message_id: UUID = Field(sa_column=sa.Column(sa.ForeignKey("message.id"), nullable=False))
    user_id: UUID = Field(sa_column=sa.Column(sa.ForeignKey("user.id"), nullable=False))
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )
    previous_revision_id: Optional[UUID] = Field(sa_column=sa.Column(sa.ForeignKey("message_revision.id")))
