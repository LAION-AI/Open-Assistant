from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel


class UserStatsTimeFrame(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    total = "total"


class UserStats(SQLModel, table=True):
    __tablename__ = "user_stats"
    __table_args__ = (
        Index("ix_user_stats__timeframe__user_id", "time_frame", "user_id", unique=True),
        Index("ix_user_stats__timeframe__rank__user_id", "time_frame", "rank", "user_id", unique=True),
    )

    time_frame: Optional[str] = Field(nullable=False, primary_key=True)
    user_id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), primary_key=True)
    )
    base_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))

    leader_score: int = 0
    modified_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )

    rank: int = Field(nullable=True)

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

    reply_ranked_1: int = 0
    reply_ranked_2: int = 0
    reply_ranked_3: int = 0

    def compute_leader_score(self) -> int:
        return (
            int(self.prompts * 0.1)
            + self.replies_assistant * 4
            + self.replies_prompter
            + self.labels_simple
            + self.labels_full * 2
            + self.rankings_total
            + self.rankings_good
            + int(self.accepted_prompts * 0.1)
            + self.accepted_replies_assistant * 4
            + self.accepted_replies_prompter
            + self.reply_ranked_1 * 9
            + self.reply_ranked_2 * 3
            + self.reply_ranked_3
        )
