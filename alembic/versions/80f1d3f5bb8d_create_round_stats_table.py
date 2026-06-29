"""create round stats table

Revision ID: 80f1d3f5bb8d
Revises: 6f0fd0b2f7a1
Create Date: 2026-06-29 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80f1d3f5bb8d'
down_revision: Union[str, Sequence[str], None] = '6f0fd0b2f7a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'round_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('round_id', sa.Integer(), nullable=False),
        sa.Column('fairways_hit', sa.Integer(), nullable=False),
        sa.Column('fairways_possible', sa.Integer(), nullable=False),
        sa.Column('greens_in_regulation', sa.Integer(), nullable=False),
        sa.Column('putts', sa.Integer(), nullable=False),
        sa.Column('penalties', sa.Integer(), nullable=False),
        sa.Column('up_and_downs', sa.Integer(), nullable=False),
        sa.Column('sand_saves', sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(['round_id'], ['rounds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_round_stats_id'), 'round_stats', ['id'], unique=False)
    op.create_index(
        op.f('ix_round_stats_round_id'),
        'round_stats',
        ['round_id'],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_round_stats_round_id'), table_name='round_stats')
    op.drop_index(op.f('ix_round_stats_id'), table_name='round_stats')
    op.drop_table('round_stats')
