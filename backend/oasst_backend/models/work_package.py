# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import false
from sqlmodel import Field, SQLModel

from .payload_column_type import PayloadContainer, payload_column_type


class WorkPackage(SQLModel, table=True):
    __tablename__ = "work_package"

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    expiry_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(), nullable=True))
    user_id: UUID = Field(nullable=True, foreign_key="user.id", index=True)
    payload_type: str = Field(nullable=False, max_length=200)
    payload: PayloadContainer = Field(sa_column=sa.Column(payload_column_type(PayloadContainer), nullable=False))
    api_client_id: UUID = Field(nullable=False, foreign_key="api_client.id")
    ack: Optional[bool] = None
    done: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))
    frontend_ref_post_id: Optional[str] = None
    thread_id: Optional[UUID] = None
    parent_post_id: Optional[UUID] = None
    collective: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))

    @property
    def expired(self) -> bool:
        return self.expiry_date is not None and datetime.utcnow() < self.expiry_date
