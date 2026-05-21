"""make_honey_type_nullable

Revision ID: 2149f6f241f4
Revises: 0001_initial
Create Date: 2026-05-21 10:37:11.282742
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2149f6f241f4'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make honey_type nullable in product_configs
    # Use batch mode required by SQLite for column alterations
    with op.batch_alter_table('product_configs', schema=None) as batch_op:
        batch_op.alter_column('honey_type',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)


def downgrade() -> None:
    # Revert honey_type back to NOT NULL
    with op.batch_alter_table('product_configs', schema=None) as batch_op:
        batch_op.alter_column('honey_type',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
