"""create practice session swing thoughts table

Revision ID: 3a5e9f8c7b21
Revises: 80f1d3f5bb8d
Create Date: 2026-06-29 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a5e9f8c7b21'
down_revision: Union[str, Sequence[str], None] = '80f1d3f5bb8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'practice_session_swing_thoughts',
        sa.Column('practice_session_id', sa.Integer(), nullable=False),
        sa.Column('swing_thought_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['practice_session_id'],
            ['practice_sessions.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['swing_thought_id'],
            ['swing_thoughts.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('practice_session_id', 'swing_thought_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('practice_session_swing_thoughts')
