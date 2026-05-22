from typing import Optional
from sqlalchemy import String, Boolean, Float, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDTimeStampedModel

class FrameType(UUIDTimeStampedModel):
    __tablename__ = "frame_types"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    brood_multiplier: Mapped[float] = mapped_column(Float, default=1.00)
    food_multiplier: Mapped[float] = mapped_column(Float, default=1.00)
    bee_multiplier: Mapped[float] = mapped_column(Float, default=1.00)
    drone_multiplier: Mapped[float] = mapped_column(Float, default=1.00)
    drone_brood_multiplier: Mapped[float] = mapped_column(Float, default=1.00)
    pollen_multiplier: Mapped[float] = mapped_column(Float, default=1.00)

class VarroaMultiplier(UUIDTimeStampedModel):
    __tablename__ = "varroa_multipliers"

    season: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # SPRING, SUMMER, AUTUMN, WINTER
    multiplier: Mapped[float] = mapped_column(Float)

class LLMConfig(UUIDTimeStampedModel):
    __tablename__ = "llm_configs"

    chatbot_system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    draft_system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    enable_weather_api: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_insights_cron: Mapped[str | None] = mapped_column(String(64), nullable=True)
    kleinunternehmer_regelung: Mapped[bool] = mapped_column(Boolean, default=False)
    gemini_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    openai_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    openrouter_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    anthropic_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    openweathermap_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    smtp_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    smtp_port: Mapped[int] = mapped_column(Integer, default=587)
    smtp_username_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    smtp_password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    smtp_from_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    smtp_use_tls: Mapped[bool] = mapped_column(Boolean, default=True)
    smtp_use_ssl: Mapped[bool] = mapped_column(Boolean, default=False)


class NumberRange(UUIDTimeStampedModel):
    __tablename__ = "number_ranges"

    key: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # e.g., "batch_number", "reserve_sample_id"
    name: Mapped[str] = mapped_column(String(100))
    prefix: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    current_value: Mapped[int] = mapped_column(default=1)
    digits: Mapped[int] = mapped_column(default=4)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


