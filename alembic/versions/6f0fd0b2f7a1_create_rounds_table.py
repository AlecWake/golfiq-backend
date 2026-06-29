"""create rounds table

Revision ID: 6f0fd0b2f7a1
Revises: a96b86bc954d
Create Date: 2026-06-28 21:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f0fd0b2f7a1'
down_revision: Union[str, Sequence[str], None] = 'a96b86bc954d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'rounds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('round_date', sa.Date(), nullable=False),
        sa.Column('course_name', sa.String(length=150), nullable=False),
        sa.Column('tee_box', sa.String(length=100), nullable=True),
        sa.Column('holes_played', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rounds_id'), 'rounds', ['id'], unique=False)
    op.create_index(op.f('ix_rounds_user_id'), 'rounds', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_rounds_user_id'), table_name='rounds')
    op.drop_index(op.f('ix_rounds_id'), table_name='rounds')
    op.drop_table('rounds')
