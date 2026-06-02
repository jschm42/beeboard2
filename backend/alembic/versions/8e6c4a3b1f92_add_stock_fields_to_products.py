"""add_stock_fields_to_products

Revision ID: 8e6c4a3b1f92
Revises: 2c7a9d5e1f44
Create Date: 2026-06-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e6c4a3b1f92'
down_revision: Union[str, None] = '2c7a9d5e1f44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if columns already exist
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('product_configs')]
    
    if 'manage_stock' not in columns:
        op.add_column('product_configs', sa.Column(
            'manage_stock',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('0')
        ))
        
    if 'stock' not in columns:
        op.add_column('product_configs', sa.Column(
            'stock',
            sa.Float(),
            nullable=False,
            server_default=sa.text('0.0')
        ))
        
    if 'min_stock' not in columns:
        op.add_column('product_configs', sa.Column(
            'min_stock',
            sa.Float(),
            nullable=False,
            server_default=sa.text('0.0')
        ))


def downgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('product_configs')]
    
    with op.batch_alter_table('product_configs', schema=None) as batch_op:
        if 'manage_stock' in columns:
            batch_op.drop_column('manage_stock')
        if 'stock' in columns:
            batch_op.drop_column('stock')
        if 'min_stock' in columns:
            batch_op.drop_column('min_stock')
