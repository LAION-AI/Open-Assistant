"""Add user id to chats table

Revision ID: b74c66553643
Revises: b365a18db6fd
Create Date: 2023-02-23 22:45:19.946188
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b74c66553643"
down_revision = "b365a18db6fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("chat", sa.Column("user_id", sa.String(), sa.ForeignKey("user.id"), nullable=True))
    op.create_index(op.f("ix_chat_user_id"), "chat", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_chat_user_id"), table_name="chat")
    op.drop_column("chat", "user_id")
