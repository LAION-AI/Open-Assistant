# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, SQLModel


class UserStats(SQLModel, table=True):
    __tablename__ = "user_stats"

    user_id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), primary_key=True)
    )
    leader_score: int = 0
    modified_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )

    reactions: int = 0  # reactions sent by user
    messages: int = 0  # messages sent by user
    upvotes: int = 0  # received upvotes (form other users)
    downvotes: int = 0  # received downvotes (from other users)
    task_reward: int = 0  # reward for task completions
    compare_wins: int = 0  # num times user's message won compare tasks
    compare_losses: int = 0  # num times users's message lost compare tasks
