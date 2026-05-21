"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-18 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Initial schema: create all tables from SQLAlchemy models
    from app.core.database import Base, engine

    Base.metadata.create_all(bind=engine)


def downgrade() -> None:
    # Drop all tables (for local/dev resets)
    from app.core.database import Base, engine

    Base.metadata.drop_all(bind=engine)
