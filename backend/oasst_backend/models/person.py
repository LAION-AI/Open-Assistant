# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel


class Person(SQLModel, table=True):
    __tablename__ = "person"
    __table_args__ = (Index("ix_person_username", "api_client_id", "username", unique=True),)

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    username: str = Field(nullable=False, max_length=128)
    auth_method: str = Field(nullable=False, max_length=128, default="local")
    display_name: str = Field(nullable=False, max_length=256)
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )
    api_client_id: UUID = Field(foreign_key="api_client.id")
