from __future__ import annotations
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDTimeStampedModel

class AIInsight(UUIDTimeStampedModel):
    __tablename__ = "ai_insights"

    apiary_id: Mapped[str] = mapped_column(ForeignKey("apiaries.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)

    # Relationships
    apiary: Mapped["Apiary"] = relationship("Apiary", back_populates="ai_insights")
