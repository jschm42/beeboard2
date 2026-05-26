"""add_currency_and_tax_rates

Revision ID: c2f4a8e71d05
Revises: 871516ca39d3
Create Date: 2026-05-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2f4a8e71d05'
down_revision: Union[str, None] = '871516ca39d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('llm_configs')]
    if 'currency' not in columns:
        op.add_column('llm_configs', sa.Column('currency', sa.String(length=10), nullable=True, server_default='EUR'))
    if 'tax_rates' not in columns:
        op.add_column('llm_configs', sa.Column('tax_rates', sa.String(length=255), nullable=True, server_default='0.0,7.0,19.0'))


def downgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('llm_configs')]
    if 'tax_rates' in columns:
        with op.batch_alter_table('llm_configs', schema=None) as batch_op:
            batch_op.drop_column('tax_rates')
    if 'currency' in columns:
        with op.batch_alter_table('llm_configs', schema=None) as batch_op:
            batch_op.drop_column('currency')
