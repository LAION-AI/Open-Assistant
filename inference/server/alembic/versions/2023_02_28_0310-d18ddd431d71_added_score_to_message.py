"""Added score to message

Revision ID: d18ddd431d71
Revises: e7a4bffb424c
Create Date: 2023-02-28 03:10:22.262395

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'd18ddd431d71'
down_revision = 'e7a4bffb424c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vote')
    op.alter_column('chat', 'user_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.add_column('message', sa.Column('score', sa.Integer(), nullable=False, server_default="0"))
    op.create_index(op.f('ix_report_message_id'), 'report', ['message_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_report_message_id'), table_name='report')
    op.drop_column('message', 'score')
    op.alter_column('chat', 'user_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_table('vote',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('message_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('score', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], name='vote_message_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='vote_pkey')
    )
    # ### end Alembic commands ###
