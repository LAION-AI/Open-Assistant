from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, Index, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = (Index("ix_user_username", "api_client_id", "username", "auth_method", unique=True),)

    id: Optional[UUID] = Field(
        sa_column=sa.Column(
            pg.UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=sa.text("gen_random_uuid()")
        ),
    )
    username: str = Field(nullable=False, max_length=128)
    auth_method: str = Field(nullable=False, max_length=128, default="local")
    display_name: str = Field(nullable=False, max_length=256)
    created_date: Optional[datetime] = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )
    api_client_id: UUID = Field(foreign_key="api_client.id")
    
    # Here `created_at` and `updated_at` fields to the User model to track when 
    # the user was created and last updated. This can be useful for auditing purposes, 
    # as well as for identifying inactive users who may need to be removed.
    created_at = Field(sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()))
    updated_at = Field(sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()))
    
    # We could also consider adding an active field to the model, which is a boolean value 
    # indicating whether the user is currently active or not. This could be useful for 
    # filtering out inactive users when querying the database.
    active = Field(sa_column=sa.Column(sa.Boolean, nullable=False, default=True))
    
    # By adding this `status` field, we will be able to store the current status of each user 
    # in the database, and use it to manage the lifecycle of users within your application. 
    # For example, you could use this field to mark a user as "approved" or "banned" based on
    # their activity or behavior.
    status: str = Field(nullable=False, max_length=128, default="pending") 
    
    # We can also add a `password` field to the User model to store the user's password. 
    # This field should be encrypted using a hashing algorithm such as bcrypt.
    password: str = Field(nullable=False, max_length=256) 
    
    # We can also add a `password_reset_token` field to the User model to store the user's 
    # password reset token. This field should be encrypted using a hashing algorithm such as 
    # bcrypt.
    password_reset_token: str = Field(nullable=True, max_length=256) 
    
    # We can also add a `password_reset_token_expiry` field to the User model to store the 
    # user's password reset token expiry date. This field should be encrypted using a hashing 
    # algorithm such as bcrypt.
    password_reset_token_expiry: str = Field(nullable=True, max_length=256)