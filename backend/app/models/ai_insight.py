from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDTimeStampedModel

class AIInsight(UUIDTimeStampedModel):
    __tablename__ = "ai_insights"

    apiary_id: Mapped[str] = mapped_column(ForeignKey("apiaries.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    apiary: Mapped["Apiary"] = relationship("Apiary", back_populates="ai_insights")


class AIInsightCronJob(UUIDTimeStampedModel):
    __tablename__ = "ai_insight_cron_jobs"

    name: Mapped[str] = mapped_column(String(160), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    cron_expression: Mapped[str] = mapped_column(String(64), default="0 */12 * * *")
    inject_weather: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    inject_locations: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    inject_apiary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    inject_hives: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    inject_log_entries: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    log_scope: Mapped[str] = mapped_column(String(20), default="IMKEREI")
    max_log_entries: Mapped[int] = mapped_column(default=20)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
