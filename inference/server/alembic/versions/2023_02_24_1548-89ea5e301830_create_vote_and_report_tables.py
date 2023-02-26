"""create vote and report tables

Revision ID: 89ea5e301830
Revises: 63322c2e41da
Create Date: 2023-02-24 15:48:50.955388

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "89ea5e301830"
down_revision = "b365a18db6fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vote",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("message_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["message.id"],
        ),
    )

    op.create_table(
        "report",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("message_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("reason", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("report_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["message.id"],
        ),
    )


def downgrade() -> None:
    pass
