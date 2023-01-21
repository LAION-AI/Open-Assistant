from datetime import datetime
from typing import Optional
from uuid import UUID, uuid1, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, SQLModel

from .payload_column_type import PayloadContainer, payload_column_type


def generate_time_uuid(node=None, clock_seq=None):
    """Create a lexicographically sortable time ordered custom (non-standard) UUID by reordering the timestamp fields of a version 1 UUID."""
    (time_low, time_mid, time_hi_version, clock_seq_hi_variant, clock_seq_low, node) = uuid1(node, clock_seq).fields
    # reconstruct 60 bit timestamp, see version 1 uuid: https://www.rfc-editor.org/rfc/rfc4122
    timestamp = (time_hi_version & 0xFFF) << 48 | (time_mid << 32) | time_low
    version = time_hi_version >> 12
    assert version == 1
    a = timestamp >> 28  # bits 28-59
    b = (timestamp >> 12) & 0xFFFF  # bits 12-27
    c = timestamp & 0xFFF  # bits 0-11 (clear version bits)
    clock_seq_hi_variant &= 0xF  # (clear variant bits)
    return UUID(fields=(a, b, c, clock_seq_hi_variant, clock_seq_low, node), version=None)


class Journal(SQLModel, table=True):
    __tablename__ = "journal"

    id: Optional[UUID] = Field(
        sa_column=sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=generate_time_uuid),
    )
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )
    user_id: Optional[UUID] = Field(nullable=True, foreign_key="user.id", index=True)
    message_id: Optional[UUID] = Field(foreign_key="message.id", nullable=True)
    api_client_id: UUID = Field(foreign_key="api_client.id")

    event_type: str = Field(nullable=False, max_length=200)
    event_payload: PayloadContainer = Field(sa_column=sa.Column(payload_column_type(PayloadContainer), nullable=False))


class JournalIntegration(SQLModel, table=True):
    __tablename__ = "journal_integration"

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    description: str = Field(max_length=512, primary_key=True)
    last_journal_id: Optional[UUID] = Field(foreign_key="journal.id", nullable=True)
    last_run: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))
    last_error: Optional[str] = Field(nullable=True)
    next_run: Optional[datetime] = Field(nullable=True)
