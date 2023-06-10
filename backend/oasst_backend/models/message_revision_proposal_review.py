from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel

class MessageRevisionProposalReview(SQLModel, table=True):
    __tablename__: str = "message_revision_proposal_review"
    __table_args__ = (
        Index(
            "ix_m_revision_review__reviewer_id__m_revision_prpsal_id", 
            "reviewer_id", 
            "message_revision_proposal_id", 
            unique=True
        ),
    )

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        )
    )
    message_revision_proposal_id: UUID = Field(nullable=False, foreign_key="message_revision_proposal.id", index=True)
    reviewer_id: Optional[UUID] = Field(nullable=False, foreign_key="user.id", index=True)
    
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp(), index=True
        )
    )

    # the only information needed
    is_upvote: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False))
    text: Optional[str] = Field(sa_column=sa.Column(sa.String()), nullable=True)

