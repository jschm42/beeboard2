"""add_bee_agent_data_source_flags

Revision ID: 5f9b7a1d2e3c
Revises: 351e2efd5baf
Create Date: 2026-05-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f9b7a1d2e3c'
down_revision: Union[str, None] = '351e2efd5baf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'bee_agent_jobs' not in tables:
        return

    columns = [c['name'] for c in inspector.get_columns('bee_agent_jobs')]
    if 'include_locations' not in columns:
        op.add_column('bee_agent_jobs', sa.Column('include_locations', sa.Boolean(), nullable=True, server_default=sa.text('1')))
    if 'include_hives' not in columns:
        op.add_column('bee_agent_jobs', sa.Column('include_hives', sa.Boolean(), nullable=True, server_default=sa.text('1')))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'bee_agent_jobs' not in tables:
        return

    columns = [c['name'] for c in inspector.get_columns('bee_agent_jobs')]
    if 'include_hives' in columns:
        with op.batch_alter_table('bee_agent_jobs', schema=None) as batch_op:
            batch_op.drop_column('include_hives')
    if 'include_locations' in columns:
        with op.batch_alter_table('bee_agent_jobs', schema=None) as batch_op:
            batch_op.drop_column('include_locations')
