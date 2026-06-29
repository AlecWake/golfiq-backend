"""create swing thoughts table

Revision ID: 372139e1dc7d
Revises: 2b539385fed9
Create Date: 2026-06-28 20:18:57.799184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '372139e1dc7d'
down_revision: Union[str, Sequence[str], None] = '2b539385fed9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('swing_thoughts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_swing_thoughts_id'), 'swing_thoughts', ['id'], unique=False)
    op.create_index(op.f('ix_swing_thoughts_user_id'), 'swing_thoughts', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_swing_thoughts_user_id'), table_name='swing_thoughts')
    op.drop_index(op.f('ix_swing_thoughts_id'), table_name='swing_thoughts')
    op.drop_table('swing_thoughts')
