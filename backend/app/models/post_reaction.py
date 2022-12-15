# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class PostReaction(SQLModel, table=True):
    __tablename__ = "post_reaction"

    post_id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("post.id"), nullable=False, primary_key=True)
    )
    person_id: UUID = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("person.id"), nullable=False, primary_key=True)
    )
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )
    payload_type: str = Field(nullable=False, max_length=200)
    payload: BaseModel = Field(sa_column=sa.Column(pg.JSONB, nullable=False))
    api_client_id: UUID = Field(nullable=False, foreign_key="api_client.id")
