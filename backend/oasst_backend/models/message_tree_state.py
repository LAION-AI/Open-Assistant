import enum
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel

# The types of States a message tree can have.
states = enum(
    INITIAL="initial",
    BREEDING_PHASE="breeding_phase",
    RANKING_PHASE="ranking_phase",
    READY_FOR_SCORING="ready_for_scoring",
    CHILDREN_SCORED="children_scored",
    FINAL="final",
)
VALID_STATES = (
    states.INITIAL,
    states.BREEDING_PHASE,
    states.RANKING_PHASE,
    states.READY_FOR_SCORING,
    states.CHILDREN_SCORED,
    states.FINAL,
)


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
