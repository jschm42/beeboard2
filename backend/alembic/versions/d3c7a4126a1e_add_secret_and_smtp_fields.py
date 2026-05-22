"""add secret and smtp fields

Revision ID: d3c7a4126a1e
Revises: b0a628329897
Create Date: 2026-05-22 10:45:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d3c7a4126a1e"
down_revision: Union[str, None] = "b0a628329897"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("llm_configs", sa.Column("gemini_api_key_encrypted", sa.Text(), nullable=True))
    op.add_column("llm_configs", sa.Column("openai_api_key_encrypted", sa.Text(), nullable=True))
    op.add_column("llm_configs", sa.Column("openrouter_api_key_encrypted", sa.Text(), nullable=True))
    op.add_column("llm_configs", sa.Column("anthropic_api_key_encrypted", sa.Text(), nullable=True))
    op.add_column("llm_configs", sa.Column("openweathermap_api_key_encrypted", sa.Text(), nullable=True))
    op.add_column("llm_configs", sa.Column("smtp_host", sa.String(length=255), nullable=True))
    op.add_column("llm_configs", sa.Column("smtp_port", sa.Integer(), nullable=True, server_default="587"))
    op.add_column("llm_configs", sa.Column("smtp_username_encrypted", sa.Text(), nullable=True))
    op.add_column("llm_configs", sa.Column("smtp_password_encrypted", sa.Text(), nullable=True))
    op.add_column("llm_configs", sa.Column("smtp_from_email", sa.String(length=255), nullable=True))
    op.add_column("llm_configs", sa.Column("smtp_use_tls", sa.Boolean(), nullable=True, server_default=sa.text("1")))
    op.add_column("llm_configs", sa.Column("smtp_use_ssl", sa.Boolean(), nullable=True, server_default=sa.text("0")))


def downgrade() -> None:
    op.drop_column("llm_configs", "smtp_use_ssl")
    op.drop_column("llm_configs", "smtp_use_tls")
    op.drop_column("llm_configs", "smtp_from_email")
    op.drop_column("llm_configs", "smtp_password_encrypted")
    op.drop_column("llm_configs", "smtp_username_encrypted")
    op.drop_column("llm_configs", "smtp_port")
    op.drop_column("llm_configs", "smtp_host")
    op.drop_column("llm_configs", "openweathermap_api_key_encrypted")
    op.drop_column("llm_configs", "anthropic_api_key_encrypted")
    op.drop_column("llm_configs", "openrouter_api_key_encrypted")
    op.drop_column("llm_configs", "openai_api_key_encrypted")
    op.drop_column("llm_configs", "gemini_api_key_encrypted")
