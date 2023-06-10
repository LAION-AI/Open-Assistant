from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4
from pydantic import PrivateAttr

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import false
from sqlmodel import Field, Index, SQLModel

class MessageRevisionProposal(SQLModel, table=True):
    __tablename__: str = "message_revision_proposal"
    __table_args__ = (Index("ix_message_revision_proposal__user_id__message_id", "user_id", "message_id", unique=True),)

    def __new__(cls, *args: Any, **kwargs: Any):
        new_object = super().__new__(cls, *args, **kwargs)
        # temporary fix until https://github.com/tiangolo/sqlmodel/issues/149 gets merged
        if not hasattr(new_object, "_upvotes") or not hasattr(new_object, "_downvotes"):
            new_object._init_private_attributes()
        return new_object

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        )
    )
    message_id: UUID = Field(nullable=False, foreign_key="message.id", index=True)
    user_id: Optional[UUID] = Field(nullable=True, foreign_key="user.id", index=True)
    
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp(), index=True
        )
    )

    text: str = Field(sa_column=sa.Column(sa.String()), nullable=False)

    deleted: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=false()))

    additions: int = Field(nullable=False)
    deletions: int = Field(nullable=False)

    _upvotes: Optional[int] = PrivateAttr(default=None)
    _downvotes: Optional[int] = PrivateAttr(default=None)

    @property
    def upvotes(self) -> Optional[int]:
        return self._upvotes

    @property
    def downvotes(self) -> Optional[int]:
        return self._downvotes
