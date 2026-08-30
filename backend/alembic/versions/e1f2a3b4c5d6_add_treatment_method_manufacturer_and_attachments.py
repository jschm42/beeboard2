"""add_treatment_method_manufacturer_and_attachments

Revision ID: e1f2a3b4c5d6
Revises: d4e5f6a7b8c9
Create Date: 2026-08-30 13:20:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Add manufacturer_info column to treatment_methods
    if 'treatment_methods' in tables:
        columns = [c['name'] for c in inspector.get_columns('treatment_methods')]
        if 'manufacturer_info' not in columns:
            with op.batch_alter_table('treatment_methods', schema=None) as batch_op:
                batch_op.add_column(sa.Column('manufacturer_info', sa.Text(), nullable=True))

    # 2. Create treatment_method_attachments table
    if 'treatment_method_attachments' not in tables:
        op.create_table(
            'treatment_method_attachments',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('treatment_method_id', sa.String(length=36), nullable=False),
            sa.Column('file_name', sa.String(length=255), nullable=False),
            sa.Column('file_path', sa.String(length=255), nullable=False),
            sa.Column('file_type', sa.String(length=100), nullable=True),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['treatment_method_id'], ['treatment_methods.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('treatment_method_attachments', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_treatment_method_attachments_treatment_method_id'), ['treatment_method_id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'treatment_method_attachments' in tables:
        with op.batch_alter_table('treatment_method_attachments', schema=None) as batch_op:
            batch_op.drop_index(batch_op.f('ix_treatment_method_attachments_treatment_method_id'))
        op.drop_table('treatment_method_attachments')

    if 'treatment_methods' in tables:
        columns = [c['name'] for c in inspector.get_columns('treatment_methods')]
        if 'manufacturer_info' in columns:
            with op.batch_alter_table('treatment_methods', schema=None) as batch_op:
                batch_op.drop_column('manufacturer_info')
