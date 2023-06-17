"""add_message_revision_proposals

Revision ID: a861415dcc8b
Revises: c181661eba3a
Create Date: 2023-06-11 10:52:05.815958

"""
import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a861415dcc8b"
down_revision = "c181661eba3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "message_revision_proposal",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "created_date", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("message_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("additions", sa.Integer(), nullable=False),
        sa.Column("deletions", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["message.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_message_revision_proposal__user_id__message_id",
        "message_revision_proposal",
        ["user_id", "message_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_revision_proposal_created_date"), "message_revision_proposal", ["created_date"], unique=False
    )
    op.create_index(
        op.f("ix_message_revision_proposal_message_id"), "message_revision_proposal", ["message_id"], unique=False
    )
    op.create_index(
        op.f("ix_message_revision_proposal_user_id"), "message_revision_proposal", ["user_id"], unique=False
    )
    op.create_table(
        "message_revision_proposal_review",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "created_date", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column("is_upvote", sa.Boolean(), nullable=False),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("message_revision_proposal_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("reviewer_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["message_revision_proposal_id"],
            ["message_revision_proposal.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_m_revision_review__reviewer_id__m_revision_prpsal_id",
        "message_revision_proposal_review",
        ["reviewer_id", "message_revision_proposal_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_message_revision_proposal_review_created_date"),
        "message_revision_proposal_review",
        ["created_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_revision_proposal_review_message_revision_proposal_id"),
        "message_revision_proposal_review",
        ["message_revision_proposal_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_revision_proposal_review_reviewer_id"),
        "message_revision_proposal_review",
        ["reviewer_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_message_revision_proposal_review_reviewer_id"), table_name="message_revision_proposal_review"
    )
    op.drop_index(
        op.f("ix_message_revision_proposal_review_message_revision_proposal_id"),
        table_name="message_revision_proposal_review",
    )
    op.drop_index(
        op.f("ix_message_revision_proposal_review_created_date"), table_name="message_revision_proposal_review"
    )
    op.drop_index(
        "ix_m_revision_review__reviewer_id__m_revision_prpsal_id", table_name="message_revision_proposal_review"
    )
    op.drop_table("message_revision_proposal_review")
    op.drop_index(op.f("ix_message_revision_proposal_user_id"), table_name="message_revision_proposal")
    op.drop_index(op.f("ix_message_revision_proposal_message_id"), table_name="message_revision_proposal")
    op.drop_index(op.f("ix_message_revision_proposal_created_date"), table_name="message_revision_proposal")
    op.drop_index("ix_message_revision_proposal__user_id__message_id", table_name="message_revision_proposal")
    op.drop_table("message_revision_proposal")
    # ### end Alembic commands ###
