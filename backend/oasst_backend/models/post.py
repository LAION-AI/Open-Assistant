# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel

from .payload_column_type import PayloadContainer, payload_column_type


class Post(SQLModel, table=True):
    __tablename__ = "post"
    __table_args__ = (Index("ix_post_frontend_post_id", "api_client_id", "frontend_post_id", unique=True),)

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    parent_id: UUID = Field(nullable=True)
    thread_id: UUID = Field(nullable=False, index=True)
    workpackage_id: UUID = Field(nullable=True, index=True)
    person_id: UUID = Field(nullable=True, foreign_key="person.id", index=True)
    role: str = Field(nullable=False, max_length=128)
    api_client_id: UUID = Field(nullable=False, foreign_key="api_client.id")
    frontend_post_id: str = Field(max_length=200, nullable=False)
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )
    payload_type: str = Field(nullable=False, max_length=200)
    payload: PayloadContainer = Field(sa_column=sa.Column(payload_column_type(PayloadContainer), nullable=True))
    lang: str = Field(nullable=False, max_length=200, default="en-US")
    depth: int = Field(sa_column=sa.Column(sa.Integer, default=0, server_default=sa.text("0"), nullable=False))
    children_count: int = Field(sa_column=sa.Column(sa.Integer, default=0, server_default=sa.text("0"), nullable=False))
