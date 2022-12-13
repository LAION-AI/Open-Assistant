from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field, SQLModel
from typing import Optional


class Labeler(SQLModel, table=True):
    __tablename__ = "labeler"
    id: Optional[int] = Field(default=None, primary_key=True)
    display_name: str
    discord_username: str
    created_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()), nullable=False)
    is_enabled: bool
    notes: str
