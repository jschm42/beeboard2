from __future__ import annotations
from sqlalchemy import String, ForeignKey, Boolean, Text, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from typing import Optional

from app.models.base import UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel

class Task(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(10), default="MEDIUM")  # LOW, MEDIUM, HIGH
    
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    location_id: Mapped[Optional[str]] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=True)
    hive_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hives.id", ondelete="CASCADE"), nullable=True)
    
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_interval: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # DAILY, WEEKLY, BIWEEKLY, MONTHLY, YEARLY

    # Relationships
    location: Mapped[Optional["Location"]] = relationship("Location", foreign_keys=[location_id])
    hive: Mapped[Optional["Hive"]] = relationship("Hive", foreign_keys=[hive_id])
