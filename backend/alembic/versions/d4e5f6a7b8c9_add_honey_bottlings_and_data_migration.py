"""add_honey_bottlings_and_data_migration

Revision ID: d4e5f6a7b8c9
Revises: 882c1743fb1a
Create Date: 2026-08-24 15:30:00.000000
"""
from typing import Sequence, Union
import uuid
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = '882c1743fb1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Create honey_bottlings table
    if 'honey_bottlings' not in tables:
        op.create_table(
            'honey_bottlings',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('honey_batch_id', sa.String(length=36), nullable=False),
            sa.Column('bottling_date', sa.Date(), nullable=False),
            sa.Column('jar_size_g', sa.Integer(), nullable=True),
            sa.Column('quantity_jars', sa.Integer(), nullable=True),
            sa.Column('quantity_kg', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['honey_batch_id'], ['honey_batches.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_honey_bottlings_honey_batch_id'), 'honey_bottlings', ['honey_batch_id'], unique=False)

    # 2. Create honey_bottling_dib_ranges table
    if 'honey_bottling_dib_ranges' not in tables:
        op.create_table(
            'honey_bottling_dib_ranges',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('bottling_id', sa.String(length=36), nullable=False),
            sa.Column('dib_label_start', sa.String(length=50), nullable=True),
            sa.Column('dib_label_end', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['bottling_id'], ['honey_bottlings.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_honey_bottling_dib_ranges_bottling_id'), 'honey_bottling_dib_ranges', ['bottling_id'], unique=False)

    # 3. Data Migration: Existing honey_batches and honey_batch_dib_ranges -> honey_bottlings
    if 'honey_batches' in tables:
        batches = conn.execute(
            sa.text("SELECT id, harvest_date, bottling_date, quantity_kg FROM honey_batches")
        ).fetchall()

        now = datetime.now(timezone.utc)
        for b in batches:
            batch_id, harvest_date, bottling_date, quantity_kg = b
            
            # Check if bottlings already exist
            existing_bottlings_count = conn.execute(
                sa.text("SELECT count(*) FROM honey_bottlings WHERE honey_batch_id = :batch_id"),
                {"batch_id": batch_id}
            ).scalar()

            if existing_bottlings_count == 0:
                # Check if batch has bottling date or dib ranges
                has_dib_ranges = False
                if 'honey_batch_dib_ranges' in tables:
                    dib_count = conn.execute(
                        sa.text("SELECT count(*) FROM honey_batch_dib_ranges WHERE honey_batch_id = :batch_id"),
                        {"batch_id": batch_id}
                    ).scalar()
                    has_dib_ranges = (dib_count > 0)

                if bottling_date is not None or has_dib_ranges:
                    bottling_id = str(uuid.uuid4())
                    b_date = bottling_date if bottling_date is not None else harvest_date
                    b_qty = quantity_kg if quantity_kg is not None else 0.0

                    conn.execute(
                        sa.text(
                            "INSERT INTO honey_bottlings (id, honey_batch_id, bottling_date, jar_size_g, quantity_jars, quantity_kg, notes, created_at, updated_at) "
                            "VALUES (:id, :honey_batch_id, :bottling_date, :jar_size_g, :quantity_jars, :quantity_kg, :notes, :created_at, :updated_at)"
                        ),
                        {
                            "id": bottling_id,
                            "honey_batch_id": batch_id,
                            "bottling_date": b_date,
                            "jar_size_g": None,
                            "quantity_jars": None,
                            "quantity_kg": b_qty,
                            "notes": None,
                            "created_at": now,
                            "updated_at": now,
                        }
                    )

                    # Migrate any DIB ranges for this batch
                    if has_dib_ranges:
                        dib_rows = conn.execute(
                            sa.text("SELECT dib_label_start, dib_label_end FROM honey_batch_dib_ranges WHERE honey_batch_id = :batch_id"),
                            {"batch_id": batch_id}
                        ).fetchall()
                        for dib in dib_rows:
                            conn.execute(
                                sa.text(
                                    "INSERT INTO honey_bottling_dib_ranges (id, bottling_id, dib_label_start, dib_label_end, created_at, updated_at) "
                                    "VALUES (:id, :bottling_id, :dib_label_start, :dib_label_end, :created_at, :updated_at)"
                                ),
                                {
                                    "id": str(uuid.uuid4()),
                                    "bottling_id": bottling_id,
                                    "dib_label_start": dib[0],
                                    "dib_label_end": dib[1],
                                    "created_at": now,
                                    "updated_at": now
                                }
                            )


def downgrade() -> None:
    op.drop_index(op.f('ix_honey_bottling_dib_ranges_bottling_id'), table_name='honey_bottling_dib_ranges')
    op.drop_table('honey_bottling_dib_ranges')
    op.drop_index(op.f('ix_honey_bottlings_honey_batch_id'), table_name='honey_bottlings')
    op.drop_table('honey_bottlings')
