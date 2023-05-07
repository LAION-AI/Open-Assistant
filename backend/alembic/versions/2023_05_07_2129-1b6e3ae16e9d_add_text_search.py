"""add text search

Revision ID: 1b6e3ae16e9d
Revises: 9db92d504f64
Create Date: 2023-05-07 21:29:35.545612
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1b6e3ae16e9d"
down_revision = "9db92d504f64"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("message", sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True))
    op.create_index("idx_search_vector", "message", ["search_vector"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_index("idx_search_vector", "message")
    op.drop_column("message", "search_vector")
