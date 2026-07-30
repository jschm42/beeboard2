"""add_created_via_mcp_to_log_entries

Revision ID: 882c1743fb1a
Revises: c159853fc0c4
Create Date: 2026-07-30 09:51:54.488236
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '882c1743fb1a'
down_revision: Union[str, None] = 'c159853fc0c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('log_entries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_via_mcp', sa.Boolean(), server_default='0', nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('log_entries', schema=None) as batch_op:
        batch_op.drop_column('created_via_mcp')

    # ### end Alembic commands ###
