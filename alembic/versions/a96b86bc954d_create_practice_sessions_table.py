"""create practice sessions table

Revision ID: a96b86bc954d
Revises: 372139e1dc7d
Create Date: 2026-06-28 20:31:10.524794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a96b86bc954d'
down_revision: Union[str, Sequence[str], None] = '372139e1dc7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('practice_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('session_date', sa.Date(), nullable=False),
    sa.Column('practice_type', sa.String(length=100), nullable=False),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('overall_rating', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_practice_sessions_id'), 'practice_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_practice_sessions_user_id'), 'practice_sessions', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_practice_sessions_user_id'), table_name='practice_sessions')
    op.drop_index(op.f('ix_practice_sessions_id'), table_name='practice_sessions')
    op.drop_table('practice_sessions')
