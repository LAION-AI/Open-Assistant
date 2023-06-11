from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from pydantic import PrivateAttr
from sqlmodel import Field, SQLModel
from uuid_extensions import uuid7

from .payload_column_type import PayloadContainer, payload_column_type


class MessageRevision(SQLModel, table=True):
    __tablename__ = "message_revision"

    id: UUID = Field(sa_column=sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid7))

    payload: Optional[PayloadContainer] = Field(
        sa_column=sa.Column(payload_column_type(PayloadContainer), nullable=True)
    )
    message_id: UUID = Field(sa_column=sa.Column(sa.ForeignKey("message.id"), nullable=False, index=True))
    user_id: Optional[UUID] = Field(sa_column=sa.Column(sa.ForeignKey("user.id"), nullable=True))
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.current_timestamp())
    )

    _user_is_author: Optional[bool] = PrivateAttr(default=None)
