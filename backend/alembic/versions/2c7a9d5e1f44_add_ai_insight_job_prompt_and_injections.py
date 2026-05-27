"""add_ai_insight_job_prompt_and_injections

Revision ID: 2c7a9d5e1f44
Revises: 9ab4d2c3e7f1
Create Date: 2026-05-27

"""
from typing import Sequence, Union

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c7a9d5e1f44'
down_revision: Union[str, None] = '9ab4d2c3e7f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import op

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'ai_insight_cron_jobs' not in tables:
        return

    columns = [c['name'] for c in inspector.get_columns('ai_insight_cron_jobs')]
    if 'prompt' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN prompt TEXT DEFAULT 'Erstelle einen praezisen KI-Insight-Bericht fuer Imker.'"))
    if 'inject_weather' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_weather BOOLEAN DEFAULT 0"))
    if 'inject_locations' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_locations BOOLEAN DEFAULT 1"))
    if 'inject_apiary' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_apiary BOOLEAN DEFAULT 1"))
    if 'inject_hives' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_hives BOOLEAN DEFAULT 1"))
    if 'inject_log_entries' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_log_entries BOOLEAN DEFAULT 1"))
    if 'log_scope' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN log_scope VARCHAR(20) DEFAULT 'IMKEREI'"))
    if 'max_log_entries' not in columns:
        conn.execute(sa.text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN max_log_entries INTEGER DEFAULT 20"))


def downgrade() -> None:
    # SQLite does not reliably support DROP COLUMN in all target environments.
    # This migration is intentionally non-destructive on downgrade.
    return
