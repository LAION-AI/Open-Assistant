from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import false
from sqlmodel import Field, SQLModel


class ApiClient(SQLModel, table=True):
    __tablename__ = "api_client"

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    api_key: str = Field(max_length=512, index=True, unique=True)
    description: str = Field(max_length=256)
    admin_email: Optional[str] = Field(max_length=256, nullable=True)
    enabled: bool = Field(default=True)
    trusted: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))
    frontend_type: str = Field(max_length=256, nullable=True)
