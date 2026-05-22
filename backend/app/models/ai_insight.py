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
