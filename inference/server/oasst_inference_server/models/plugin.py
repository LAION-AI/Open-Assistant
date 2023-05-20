from uuid import uuid4

from sqlmodel import Field, SQLModel


class DbPluginOAuthProvider(SQLModel, table=True):
    __tablename__ = "plugin_oauth_provider"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    provider: str = Field(..., nullable=False, index=True)

    client_id: str = Field(..., nullable=False)
    client_secret: str = Field(..., nullable=False)
