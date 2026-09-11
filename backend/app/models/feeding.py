from __future__ import annotations
from sqlalchemy import String, ForeignKey, Float, Text, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from typing import Optional, List

from app.models.base import UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel

class FeedType(UUIDTimeStampedModel):
    __tablename__ = "feed_types"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(20), default="kg")  # kg, gr, l, etc.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    feedings: Mapped[List["Feeding"]] = relationship(
        "Feeding",
        back_populates="feed_type"
    )

class Feeding(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "feedings"

    hive_id: Mapped[str] = mapped_column(ForeignKey("hives.id", ondelete="CASCADE"), index=True)
    feed_type_id: Mapped[str] = mapped_column(ForeignKey("feed_types.id", ondelete="RESTRICT"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[float] = mapped_column(Float)
    fed_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    hive: Mapped["Hive"] = relationship("Hive", back_populates="feedings", foreign_keys=[hive_id])
    feed_type: Mapped["FeedType"] = relationship("FeedType", back_populates="feedings")
