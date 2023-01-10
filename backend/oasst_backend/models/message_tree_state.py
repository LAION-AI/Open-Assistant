from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel


class States(str, Enum):
    """States of the Open-Assistant message tree state machine."""

    INITIAL_PROMPT_REVIEW = "initial_prompt_review"
    """In this state the message tree consists only of a single inital prompt root node.
    Initial prompt labeling tasks will determine if the tree goes into `breeding_phase` or
    `aborted_low_grade`."""

    BREEDING_PHASE = "breeding_phase"
    """Assistant & prompter human demonstrations are collected. Concurrently labeling tasks
    are handed out to check if the quality of the replies surpasses the minimum acceptable
    quality.
    When the required number of messages passing the initial labelling-quality check has been
    collected the tree will enter `ranking_phase`. If too many poor-quality labelling responses
    are received the tree can also enter the `aborted_low_grade` state."""

    RANKING_PHASE = "ranking_phase"
    """The tree has been successfully populated with the desired number of messages. Ranking
    tasks are now handed out for all nodes with more than one child."""

    READY_FOR_SCORING = "ready_for_scoring"
    """Required ranking responses have been collected and the scoring algorithm can now
    compute the aggergated ranking scores that will appear in the dataset."""

    READY_FOR_EXPORT = "ready_for_export"
    """The Scoring algorithm computed rankings scores for all childern. The message tree can be
    exported as part of an Open-Assistant message tree dataset."""

    SCORING_FAILED = "scoring_failed"
    """An exception occured in the scoring algorithm."""

    ABORTED_LOW_GRADE = "aborted_low_grade"
    """The system received too many bad reviews and stopped handing out tasks for this message tree."""

    HALTED_BY_MODERATOR = "halted_by_moderator"
    """A moderator decided to manually halt the message tree construction process."""


VALID_STATES = (
    States.INITIAL_PROMPT_REVIEW,
    States.BREEDING_PHASE,
    States.RANKING_PHASE,
    States.READY_FOR_SCORING,
    States.READY_FOR_EXPORT,
    States.ABORTED_LOW_GRADE,
)

TERMINAL_STATES = (States.READY_FOR_EXPORT, States.ABORTED_LOW_GRADE, States.SCORING_FAILED, States.HALTED_BY_MODERATOR)


class MessageTreeState(SQLModel, table=True):
    __tablename__ = "message_tree_state"
    __table_args__ = (Index("ix_message_tree_state_tree_id", "message_tree_id", unique=True),)

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    message_tree_id: UUID = Field(nullable=False, index=True)
    state: str = Field(nullable=False, max_length=128)
    goal_tree_size: int = Field(nullable=False)
    current_num_non_filtered_messages: int = Field(nullable=False)
    max_depth: int = Field(nullable=False)
