"""v1 db structure

Revision ID: cd7de470586e
Revises: 23e5fea252dd
Create Date: 2022-12-15 11:15:32.830225

"""
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision = "cd7de470586e"
down_revision = "23e5fea252dd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # remove database objects
    op.drop_index(op.f("prompt_labeler_id"), table_name="prompt")
    op.drop_table("prompt")
    op.drop_table("labeler")
    op.drop_index(op.f("ix_service_client_api_key"), table_name="service_client")
    op.drop_table("service_client")

    # wreate new database structure
    op.create_table(
        "api_client",
        sa.Column("id", UUID(as_uuid=True), default=uuid.uuid4, server_default=sa.text("gen_random_uuid()")),
        sa.Column("api_key", sa.String(512), nullable=False),
        sa.Column("description", sa.String(256), nullable=False),
        sa.Column("admin_email", sa.String(256), nullable=True),
        sa.Column("enabled", sa.Boolean, default=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_client_api_key"), "api_client", ["api_key"], unique=True)

    op.create_table(
        "person",
        sa.Column("id", UUID(as_uuid=True), default=uuid.uuid4, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(128), nullable=False),  # unique in combination with api_client_id
        sa.Column("display_name", sa.String(256), nullable=False),  # cached last seen display_name
        sa.Column("created_date", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("api_client_id", UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["api_client_id"], ["api_client.id"]),
    )
    op.create_index(op.f("ix_person_username"), "person", ["api_client_id", "username"], unique=True)

    op.create_table(
        "person_stats",
        sa.Column("person_id", UUID(as_uuid=True)),
        sa.Column("leader_score", sa.Integer, default=0, nullable=False),  # determines position on leader board
        sa.Column("modified_date", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("reactions", sa.Integer, default=0, nullable=False),  # reactions sent by user
        sa.Column("posts", sa.Integer, default=0, nullable=False),  # posts sent by user
        sa.Column("upvotes", sa.Integer, default=0, nullable=False),  # received upvotes (form other users)
        sa.Column("downvotes", sa.Integer, default=0, nullable=False),  # received downvotes (from other users)
        sa.Column("work_reward", sa.Integer, default=0, nullable=False),  # reward for workpackage completions
        sa.Column("compare_wins", sa.Integer, default=0, nullable=False),  # num times user's post won compare tasks
        sa.Column("compare_losses", sa.Integer, default=0, nullable=False),  # num times users's post lost compare tasks
        sa.PrimaryKeyConstraint("person_id"),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"]),
    )

    op.create_table(
        "work_package",
        sa.Column("id", UUID(as_uuid=True), default=uuid.uuid4, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_date", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("expiry_date", sa.DateTime(), nullable=True),
        sa.Column("person_id", UUID(as_uuid=True), nullable=True),
        sa.Column("payload_type", sa.String(200), nullable=False),  # deserialization hint & dbg aid
        sa.Column("payload", JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("api_client_id", UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"]),
        sa.ForeignKeyConstraint(["api_client_id"], ["api_client.id"]),
    )
    op.create_index(op.f("ix_work_package_person_id"), "work_package", ["person_id"], unique=False)

    op.create_table(
        "post",
        sa.Column("id", UUID(as_uuid=True), default=uuid.uuid4, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parent_id", UUID(as_uuid=True), nullable=True),  # root posts have NULL parent
        sa.Column("thread_id", UUID(as_uuid=True), nullable=False),  # id of thread root
        sa.Column("workpackage_id", UUID(as_uuid=True), nullable=True),  # workpackage id to pass to handler on reply
        sa.Column("person_id", UUID(as_uuid=True), nullable=True),  # sender (recipients are part of payload)
        sa.Column("api_client_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(128), nullable=False),  # 'assistant', 'user' or something else
        sa.Column("frontend_post_id", sa.String(200), nullable=False),  # unique together with api_client_id
        sa.Column("created_date", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("payload_type", sa.String(200), nullable=False),  # deserialization hint & dbg aid
        sa.Column("payload", JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"]),
        sa.ForeignKeyConstraint(["api_client_id"], ["api_client.id"]),
    )
    op.create_index(op.f("ix_post_frontend_post_id"), "post", ["api_client_id", "frontend_post_id"], unique=True)
    op.create_index(op.f("ix_post_thread_id"), "post", ["thread_id"], unique=False)
    op.create_index(op.f("ix_post_workpackage_id"), "post", ["workpackage_id"], unique=False)
    op.create_index(op.f("ix_post_person_id"), "post", ["person_id"], unique=False)

    op.create_table(
        "post_reaction",
        sa.Column("post_id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),  # sender (recipients are part of payload)
        sa.Column("created_date", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("payload_type", sa.String(200), nullable=False),  # deserialization hint & dbg aid
        sa.Column("payload", JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("api_client_id", UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("post_id", "person_id"),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"]),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"]),
        sa.ForeignKeyConstraint(["api_client_id"], ["api_client.id"]),
    )


def downgrade() -> None:
    op.drop_table("post_reaction")

    op.drop_index("ix_post_person_id")
    op.drop_index("ix_post_workpackage_id")
    op.drop_index("ix_post_thread_id")
    op.drop_index("ix_post_frontend_post_id")
    op.drop_table("post")

    op.drop_index("ix_work_package_person_id")
    op.drop_table("work_package")

    op.drop_table("person_stats")

    op.drop_index("ix_person_username")
    op.drop_table("person")

    op.drop_index("ix_api_client_api_key")
    op.drop_table("api_client")

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
