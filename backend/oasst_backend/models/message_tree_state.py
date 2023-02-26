from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel


class State(str, Enum):
    """States of the Open-Assistant message tree state machine."""

    INITIAL_PROMPT_REVIEW = "initial_prompt_review"
    """In this state the message tree consists only of a single initial prompt root node.
    Initial prompt labeling tasks will determine if the tree goes into `growing` or
    `aborted_low_grade` state."""

    GROWING = "growing"
    """Assistant & prompter human demonstrations are collected. Concurrently labeling tasks
    are handed out to check if the quality of the replies surpasses the minimum acceptable
    quality.
    When the required number of messages passing the initial labelling-quality check has been
    collected the tree will enter `ranking`. If too many poor-quality labelling responses
    are received the tree can also enter the `aborted_low_grade` state."""

    RANKING = "ranking"
    """The tree has been successfully populated with the desired number of messages. Ranking
    tasks are now handed out for all nodes with more than one child."""

    READY_FOR_SCORING = "ready_for_scoring"
    """Required ranking responses have been collected and the scoring algorithm can now
    compute the aggergated ranking scores that will appear in the dataset."""

    READY_FOR_EXPORT = "ready_for_export"
    """The Scoring algorithm computed rankings scores for all children. The message tree can be
    exported as part of an Open-Assistant message tree dataset."""

    SCORING_FAILED = "scoring_failed"
    """An exception occurred in the scoring algorithm."""

    ABORTED_LOW_GRADE = "aborted_low_grade"
    """The system received too many bad reviews and stopped handing out tasks for this message tree."""

    HALTED_BY_MODERATOR = "halted_by_moderator"
    """A moderator decided to manually halt the message tree construction process."""

    BACKLOG_RANKING = "backlog_ranking"
    """Imported tree ready to be activated and ranked by users (currently inactive)."""

    PROMPT_LOTTERY_WAITING = "prompt_lottery_waiting"
    """Initial prompt has passed spam check, waiting to be drawn to grow."""


VALID_STATES = (
    State.INITIAL_PROMPT_REVIEW,
    State.GROWING,
    State.RANKING,
    State.READY_FOR_SCORING,
    State.READY_FOR_EXPORT,
    State.ABORTED_LOW_GRADE,
    State.BACKLOG_RANKING,
)

TERMINAL_STATES = (
    State.READY_FOR_EXPORT,
    State.ABORTED_LOW_GRADE,
    State.SCORING_FAILED,
    State.HALTED_BY_MODERATOR,
    State.BACKLOG_RANKING,
    State.PROMPT_LOTTERY_WAITING,
)


class MessageTreeState(SQLModel, table=True):
    __tablename__ = "message_tree_state"
    __table_args__ = (Index("ix_message_tree_state__lang__state", "state", "lang", unique=False),)

    message_tree_id: UUID = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("message.id"), primary_key=True)
    )
    goal_tree_size: int = Field(nullable=False)
    max_depth: int = Field(nullable=False)
    max_children_count: int = Field(nullable=False)
    state: str = Field(nullable=False, max_length=128)
    active: bool = Field(nullable=False, index=True)
    origin: str = Field(sa_column=sa.Column(sa.String(1024), nullable=True))
    won_prompt_lottery_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))
    lang: str = Field(sa_column=sa.Column(sa.String(32), nullable=False))
