"""merge heads

Revision ID: 351e2efd5baf
Revises: 8d9c5f1a2b31, c2f4a8e71d05
Create Date: 2026-05-27 10:44:49.007491
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '351e2efd5baf'
down_revision: Union[str, None] = ('8d9c5f1a2b31', 'c2f4a8e71d05')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
