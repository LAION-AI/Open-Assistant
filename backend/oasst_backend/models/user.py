from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from oasst_shared.schemas import protocol
from sqlmodel import AutoString, Field, Index, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = (
        Index("ix_user_username", "api_client_id", "username", "auth_method", unique=True),
        Index("ix_user_display_name_id", "display_name", "id", unique=True),
    )

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    username: str = Field(nullable=False, max_length=128)
    auth_method: str = Field(nullable=False, max_length=128, default="local")
    display_name: str = Field(nullable=False, max_length=256)
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp())
    )
    api_client_id: UUID = Field(foreign_key="api_client.id")
    enabled: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.true()))
    notes: str = Field(sa_column=sa.Column(AutoString(length=1024), nullable=False, server_default=""))
    deleted: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.false()))
    show_on_leaderboard: bool = Field(sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.true()))

    # only used for time span "total"
    streak_last_day_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.current_timestamp())
    )
    streak_days: Optional[int] = Field(nullable=True)
    last_activity_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.current_timestamp())
    )

    # terms of service acceptance date
    tos_acceptance_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))

    def to_protocol_frontend_user(self):
        return protocol.FrontEndUser(
            user_id=self.id,
            id=self.username,
            display_name=self.display_name,
            auth_method=self.auth_method,
            enabled=self.enabled,
            deleted=self.deleted,
            notes=self.notes,
            created_date=self.created_date,
            show_on_leaderboard=self.show_on_leaderboard,
            streak_days=self.streak_days,
            streak_last_day_date=self.streak_last_day_date,
            last_activity_date=self.last_activity_date,
            tos_acceptance_date=self.tos_acceptance_date,
        )


class Account(SQLModel, table=True):
    __tablename__ = "account"
    __table_args__ = (Index("provider", "provider_account_id", unique=True),)

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    user_id: UUID = Field(foreign_key="user.id")
    provider: str = Field(nullable=False, max_length=128, default="email")  # discord or email
    provider_account_id: str = Field(nullable=False, max_length=128)
