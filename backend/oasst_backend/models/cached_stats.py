from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import AutoString, Field, SQLModel


class CachedStats(SQLModel, table=True):
    __tablename__ = "cached_stats"

    name: str = Field(sa_column=sa.Column(AutoString(length=128), primary_key=True))

    modified_date: datetime | None = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )

    stats: dict | list | None = Field(None, sa_column=sa.Column(pg.JSONB, nullable=False))
