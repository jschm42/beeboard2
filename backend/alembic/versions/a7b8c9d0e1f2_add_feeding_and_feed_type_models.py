"""add_feeding_and_feed_type_models

Revision ID: a7b8c9d0e1f2
Revises: f2a3b4c5d6e7
Create Date: 2026-09-11 14:35:00.000000
"""
from typing import Sequence, Union
import uuid
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'feed_types' not in tables:
        op.create_table(
            'feed_types',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('name', sa.String(length=120), nullable=False, unique=True),
            sa.Column('unit', sa.String(length=20), nullable=False, server_default='kg'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
        )
        op.create_index('ix_feed_types_name', 'feed_types', ['name'], unique=True)

        # Seed initial feed types
        now = datetime.now(timezone.utc)
        feed_types_table = sa.table(
            'feed_types',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('unit', sa.String),
            sa.column('is_active', sa.Boolean),
            sa.column('description', sa.Text),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        )
        op.bulk_insert(
            feed_types_table,
            [
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Zuckerwasser 1:1',
                    'unit': 'l',
                    'is_active': True,
                    'description': 'Zucker-Wasser-Lösung im Verhältnis 1:1 für Reiz- oder Frühjahrsfütterung',
                    'created_at': now,
                    'updated_at': now,
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Zuckerwasser 3:2',
                    'unit': 'l',
                    'is_active': True,
                    'description': 'Dickflüssige Zucker-Wasser-Lösung 3:2 zur Auffütterung',
                    'created_at': now,
                    'updated_at': now,
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Invertzuckersirup',
                    'unit': 'l',
                    'is_active': True,
                    'description': 'Gebrauchsfertiger flüssiger Bienenfutter-Sirup (z.B. Apiinvert)',
                    'created_at': now,
                    'updated_at': now,
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Futterteig',
                    'unit': 'kg',
                    'is_active': True,
                    'description': 'Fester Futterteig (z.B. Apifonda) für Not- oder Ablegerfütterung',
                    'created_at': now,
                    'updated_at': now,
                },
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Bio-Futterteig',
                    'unit': 'kg',
                    'is_active': True,
                    'description': 'Zertifizierter Bio-Futterteig',
                    'created_at': now,
                    'updated_at': now,
                },
            ]
        )

    if 'feedings' not in tables:
        op.create_table(
            'feedings',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('hive_id', sa.String(length=36), sa.ForeignKey('hives.id', ondelete='CASCADE'), nullable=False),
            sa.Column('feed_type_id', sa.String(length=36), sa.ForeignKey('feed_types.id', ondelete='RESTRICT'), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('fed_by', sa.String(length=120), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('apiary_id', sa.String(length=36), sa.ForeignKey('apiaries.id', ondelete='CASCADE'), nullable=True),
            sa.Column('created_by_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
        )
        op.create_index('ix_feedings_hive_id', 'feedings', ['hive_id'], unique=False)
        op.create_index('ix_feedings_feed_type_id', 'feedings', ['feed_type_id'], unique=False)
        op.create_index('ix_feedings_date', 'feedings', ['date'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'feedings' in tables:
        op.drop_table('feedings')
    if 'feed_types' in tables:
        op.drop_table('feed_types')
