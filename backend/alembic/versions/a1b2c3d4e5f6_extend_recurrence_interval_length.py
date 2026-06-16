"""extend_recurrence_interval_length

Revision ID: a1b2c3d4e5f6
Revises: abade8f4b765
Create Date: 2026-06-16

Extends recurrence_interval column from VARCHAR(20) to VARCHAR(30)
to support the new EVERY_N_DAYS format (e.g. EVERY_14_DAYS).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'abade8f4b765'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'tasks' not in tables:
        return

    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column(
            'recurrence_interval',
            existing_type=sa.String(20),
            type_=sa.String(30),
            existing_nullable=True
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'tasks' not in tables:
        return

    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column(
            'recurrence_interval',
            existing_type=sa.String(30),
            type_=sa.String(20),
            existing_nullable=True
        )
