from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, SQLModel


class UserStatsTimeFrame(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    total = "total"


class UserStats(SQLModel, table=True):
    __tablename__ = "user_stats"

    user_id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), primary_key=True)
    )
    time_frame: Optional[str] = Field(nullable=False, primary_key=True)

    leader_score: int = 0
    modified_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )

    prompts: int = 0
    replies_assistant: int = 0
    replies_prompter: int = 0
    labels_simple: int = 0
    labels_full: int = 0
    rankings_total: int = 0
    rankings_good: int = 0

    accepted_prompts: int = 0
    accepted_replies_assistant: int = 0
    accepted_replies_prompter: int = 0

    reply_assistant_ranked_1: int = 0
    reply_assistant_ranked_2: int = 0
    reply_assistant_ranked_3: int = 0

    reply_prompter_ranked_1: int = 0
    reply_prompter_ranked_2: int = 0
    reply_prompter_ranked_3: int = 0

    # only used for time span "total"
    streak_last_day_date: Optional[datetime] = Field(nullable=True)
    streak_days: Optional[int] = Field(nullable=True)
