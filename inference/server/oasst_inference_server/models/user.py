from uuid import uuid4

from sqlmodel import Field, Index, SQLModel


class DbUser(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = (Index("provider", "provider_account_id", unique=True),)

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    provider: str = Field(index=True)
    provider_account_id: str = Field(index=True)

    display_name: str = Field(nullable=False, max_length=256)


class DbRefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"

    token_hash: str = Field(nullable=False, primary_key=True)
    user_id: str = Field(nullable=False, index=True, foreign_key="user.id")
    enabled: bool = Field(nullable=False, default=True)
