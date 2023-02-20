from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from oasst_shared.utils import utcnow
from sqlalchemy import false
from sqlmodel import Field, SQLModel

from .payload_column_type import PayloadContainer, payload_column_type


class Task(SQLModel, table=True):
    __tablename__ = "task"

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.current_timestamp()
        ),
    )
    expiry_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))
    user_id: Optional[UUID] = Field(nullable=True, foreign_key="user.id", index=True)
    payload_type: str = Field(nullable=False, max_length=200)
    payload: PayloadContainer = Field(sa_column=sa.Column(payload_column_type(PayloadContainer), nullable=False))
    api_client_id: UUID = Field(nullable=False, foreign_key="api_client.id")
    ack: Optional[bool] = None
    done: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))
    skipped: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))
    skip_reason: Optional[str] = Field(nullable=True, max_length=512)
    frontend_message_id: Optional[str] = None
    message_tree_id: Optional[UUID] = None
    parent_message_id: Optional[UUID] = None
    collective: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))

    @property
    def expired(self) -> bool:
        return self.expiry_date is not None and utcnow() > self.expiry_date
