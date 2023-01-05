from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import false
from sqlmodel import Field, Index, SQLModel

INITIAL = "initial"
BREEDING_PHASE = "breeding_phase"
RANKING_PHASE = "ranking_phase"
READY_FOR_SCORING = "ready_for_scoring"
CHILDREN_SCORED = "children_scored"
FINAL = "final"

VALID_STATES = (INITIAL, BREEDING_PHASE, RANKING_PHASE, READY_FOR_SCORING, CHILDREN_SCORED, FINAL)

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
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )
    current_num_non_filtered_messages: int = Field(nullable=False)
    max_depth: int = Field(nullable=False)
    deleted: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))
