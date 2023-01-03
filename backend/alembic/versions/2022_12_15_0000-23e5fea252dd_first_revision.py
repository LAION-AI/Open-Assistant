"""first revision

Revision ID: 23e5fea252dd
Revises:
Create Date: 2022-12-12 12:47:28.801354

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "23e5fea252dd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_client",
        sa.Column("id", sa.Integer, sa.Identity()),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("service_admin_email", sa.String(128), nullable=True),
        sa.Column("api_key", sa.String(300), nullable=False),
        sa.Column("can_append", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("can_write", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("can_delete", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("can_read", sa.Boolean, nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_client_api_key"), "service_client", ["api_key"], unique=True)

    op.create_table(
        "labeler",
        sa.Column("id", sa.Integer, sa.Identity()),
        sa.Column("display_name", sa.String(96), nullable=False),
        sa.Column("discord_username", sa.String(96), nullable=True),
        sa.Column(
            "created_date",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notes", sa.String(10 * 1024), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("discord_username"),
    )

    op.create_table(
        "prompt",
        sa.Column("id", sa.Integer, sa.Identity()),
        sa.Column("labeler_id", sa.Integer, nullable=False),
        sa.Column("prompt", sa.Text, nullable=False),
        sa.Column("response", sa.Text, nullable=True),
        sa.Column("lang", sa.String(32), nullable=True),
        sa.Column(
            "created_date",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.ForeignKeyConstraint(
            ["labeler_id"],
            ["labeler.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("prompt_labeler_id"), "prompt", ["labeler_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("prompt_labeler_id"), table_name="prompt")
    op.drop_table("prompt")

    op.drop_table("labeler")

    op.drop_index(op.f("ix_service_client_api_key"), table_name="service_client")
    op.drop_table("service_client")
