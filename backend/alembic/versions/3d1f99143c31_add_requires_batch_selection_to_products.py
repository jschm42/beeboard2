"""add_requires_batch_selection_to_products

Revision ID: 3d1f99143c31
Revises: 2149f6f241f4
Create Date: 2026-05-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d1f99143c31'
down_revision: Union[str, None] = '2149f6f241f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column already exists (useful if DB was created via create_all)
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('product_configs')]
    if 'requires_batch_selection' not in columns:
        op.add_column('product_configs', sa.Column(
            'requires_batch_selection',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('0')
        ))


def downgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('product_configs')]
    if 'requires_batch_selection' in columns:
        with op.batch_alter_table('product_configs', schema=None) as batch_op:
            batch_op.drop_column('requires_batch_selection')
