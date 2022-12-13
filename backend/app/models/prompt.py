from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field, SQLModel
from typing import Optional


class Prompt(SQLModel, table=True):
    __tablename__ = "prompt"
    id: Optional[int] = Field(default=None, primary_key=True)
    labeler_id: Optional[int] = Field(default=None, foreign_key="labeler.id")
    prompt: str
    response: Optional[str]
    lang: Optional[str]
    created_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()), nullable=False)
 