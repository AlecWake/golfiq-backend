"""create hole scores table

Revision ID: 4c7a1b8e9f20
Revises: 3a5e9f8c7b21
Create Date: 2026-07-06 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c7a1b8e9f20'
down_revision: Union[str, Sequence[str], None] = '3a5e9f8c7b21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'hole_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('round_id', sa.Integer(), nullable=False),
        sa.Column('hole_number', sa.Integer(), nullable=False),
        sa.Column('strokes', sa.Integer(), nullable=False),
        sa.Column('putts', sa.Integer(), nullable=False),
        sa.Column('fairway_hit', sa.Boolean(), nullable=False),
        sa.Column('green_in_regulation', sa.Boolean(), nullable=False),
        sa.Column('penalty_strokes', sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(['round_id'], ['rounds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'round_id',
            'hole_number',
            name='uq_hole_scores_round_hole',
        ),
    )
    op.create_index(op.f('ix_hole_scores_id'), 'hole_scores', ['id'], unique=False)
    op.create_index(
        op.f('ix_hole_scores_round_id'),
        'hole_scores',
        ['round_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_hole_scores_round_id'), table_name='hole_scores')
    op.drop_index(op.f('ix_hole_scores_id'), table_name='hole_scores')
    op.drop_table('hole_scores')
