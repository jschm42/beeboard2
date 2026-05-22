"""add_read_status_to_ai_insights

Revision ID: 8d9c5f1a2b31
Revises: b0a628329897
Create Date: 2026-05-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d9c5f1a2b31'
down_revision: Union[str, None] = 'b0a628329897'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('ai_insights')]

    if 'is_read' not in columns:
        op.add_column(
            'ai_insights',
            sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('0'))
        )

    if 'read_at' not in columns:
        op.add_column(
            'ai_insights',
            sa.Column('read_at', sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('ai_insights')]

    if 'read_at' in columns:
        with op.batch_alter_table('ai_insights', schema=None) as batch_op:
            batch_op.drop_column('read_at')

    if 'is_read' in columns:
        with op.batch_alter_table('ai_insights', schema=None) as batch_op:
            batch_op.drop_column('is_read')
