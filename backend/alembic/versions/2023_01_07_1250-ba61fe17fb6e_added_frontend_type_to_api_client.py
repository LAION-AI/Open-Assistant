"""added frontend_type to api_client

Revision ID: ba61fe17fb6e
Revises: 20cd871f4ec7
Create Date: 2023-01-07 12:50:32.195930

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ba61fe17fb6e"
down_revision = "20cd871f4ec7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("api_client", sa.Column("frontend_type", sa.String(256), nullable=True))


def downgrade() -> None:
    op.drop_column("api_client", "frontend_type")
