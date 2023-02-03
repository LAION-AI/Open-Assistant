from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel


class TrollStats(SQLModel, table=True):
    __tablename__ = "troll_stats"
    __table_args__ = (Index("ix_troll_stats__timeframe__user_id", "time_frame", "user_id", unique=True),)

    time_frame: Optional[str] = Field(nullable=False, primary_key=True)
    user_id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    )
    base_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))

    troll_score: int = 0
    modified_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )

    rank: int = Field(nullable=True)

    red_flags: int = 0  # num reported messages of user
    upvotes: int = 0  # num up-voted messages of user
    downvotes: int = 0  # num down-voted messages of user

    spam_prompts: int = 0

    quality: float = Field(nullable=True)
    humor: float = Field(nullable=True)
    toxicity: float = Field(nullable=True)
    violence: float = Field(nullable=True)
    helpfulness: float = Field(nullable=True)

    spam: int = 0
    lang_mismach: int = 0
    not_appropriate: int = 0
    pii: int = 0
    hate_speech: int = 0
    sexual_content: int = 0
    political_content: int = 0

    def compute_troll_score(self) -> int:
        return (
            self.red_flags * 3
            - self.upvotes
            + self.downvotes
            + self.spam_prompts
            + self.lang_mismach
            + self.not_appropriate
            + self.pii
            + self.hate_speech
            + self.sexual_content
            + self.political_content
        )
