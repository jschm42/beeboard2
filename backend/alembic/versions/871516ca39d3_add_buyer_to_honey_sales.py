"""add_buyer_to_honey_sales

Revision ID: 871516ca39d3
Revises: 3d1f99143c31
Create Date: 2026-05-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '871516ca39d3'
down_revision: Union[str, None] = '3d1f99143c31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column already exists (useful if DB was created via create_all)
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('honey_sales')]
    if 'buyer' not in columns:
        op.add_column('honey_sales', sa.Column('buyer', sa.String(length=200), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('honey_sales')]
    if 'buyer' in columns:
        with op.batch_alter_table('honey_sales', schema=None) as batch_op:
            batch_op.drop_column('buyer')
