"""empty message

Revision ID: 06cc56417e69
Revises: 05975b274a81, aac6b2f66006
Create Date: 2023-01-10 20:52:22.608278

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '06cc56417e69'
down_revision = ('05975b274a81', 'aac6b2f66006')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
