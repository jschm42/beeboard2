"""add_default_batch_to_products

Revision ID: abade8f4b765
Revises: 59eeb84b4bce
Create Date: 2026-06-16 09:00:08.944641
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abade8f4b765'
down_revision: Union[str, None] = '59eeb84b4bce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('product_configs')]
    
    if 'default_batch_id' not in columns:
        with op.batch_alter_table('product_configs', schema=None) as batch_op:
            batch_op.add_column(sa.Column('default_batch_id', sa.String(length=36), nullable=True))
            batch_op.create_foreign_key(
                'fk_product_configs_default_batch_id_honey_batches',
                'honey_batches',
                ['default_batch_id'],
                ['id'],
                ondelete='SET NULL'
            )


def downgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('product_configs')]
    
    if 'default_batch_id' in columns:
        with op.batch_alter_table('product_configs', schema=None) as batch_op:
            batch_op.drop_constraint('fk_product_configs_default_batch_id_honey_batches', type_='foreignkey')
            batch_op.drop_column('default_batch_id')
