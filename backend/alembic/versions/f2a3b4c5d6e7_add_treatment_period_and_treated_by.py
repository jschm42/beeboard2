"""add_treatment_period_and_treated_by

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-08-30 13:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a3b4c5d6e7'
down_revision: Union[str, None] = 'e1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'treatments' in tables:
        columns = [c['name'] for c in inspector.get_columns('treatments')]
        with op.batch_alter_table('treatments', schema=None) as batch_op:
            if 'end_date' not in columns:
                batch_op.add_column(sa.Column('end_date', sa.Date(), nullable=True))
            if 'treated_by' not in columns:
                batch_op.add_column(sa.Column('treated_by', sa.String(length=120), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'treatments' in tables:
        columns = [c['name'] for c in inspector.get_columns('treatments')]
        with op.batch_alter_table('treatments', schema=None) as batch_op:
            if 'treated_by' in columns:
                batch_op.drop_column('treated_by')
            if 'end_date' in columns:
                batch_op.drop_column('end_date')
