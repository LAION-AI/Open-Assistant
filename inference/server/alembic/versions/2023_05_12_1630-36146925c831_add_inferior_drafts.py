"""add_inferior_drafts

Revision ID: 36146925c831
Revises: 19178d144265
Create Date: 2023-05-12 16:30:24.966766

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "36146925c831"
down_revision = "19178d144265"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("message", sa.Column("inferior_drafts", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("message", "inferior_drafts")
    # ### end Alembic commands ###
