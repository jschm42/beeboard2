"""create_ai_insight_cron_jobs

Revision ID: 9ab4d2c3e7f1
Revises: 5f9b7a1d2e3c
Create Date: 2026-05-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ab4d2c3e7f1'
down_revision: Union[str, None] = '5f9b7a1d2e3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'ai_insight_cron_jobs' in tables:
        return

    op.create_table(
        'ai_insight_cron_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('cron_expression', sa.String(length=64), nullable=False, server_default='0 */12 * * *'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_insight_cron_jobs_name'), 'ai_insight_cron_jobs', ['name'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'ai_insight_cron_jobs' not in tables:
        return

    op.drop_index(op.f('ix_ai_insight_cron_jobs_name'), table_name='ai_insight_cron_jobs')
    op.drop_table('ai_insight_cron_jobs')
