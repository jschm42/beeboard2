from __future__ import annotations
from sqlalchemy import String, Date, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date

from app.models.base import UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel

class HoneyBatch(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "honey_batches"

    batch_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    honey_type: Mapped[str] = mapped_column(String(100), index=True)
    harvest_date: Mapped[date] = mapped_column(Date)
    bottling_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    quantity_kg: Mapped[float] = mapped_column(Float)
    water_content_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    heating_temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    best_before_date: Mapped[date] = mapped_column(Date)
    is_exact_date: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    dib_ranges: Mapped[List[HoneyBatchDIBRange]] = relationship(
        "HoneyBatchDIBRange",
        back_populates="honey_batch",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    
    @property
    def dib_label_start(self) -> Optional[str]:
        return self.dib_ranges[0].dib_label_start if self.dib_ranges else None

    @property
    def dib_label_end(self) -> Optional[str]:
        return self.dib_ranges[0].dib_label_end if self.dib_ranges else None
    
    reserve_sample_taken: Mapped[bool] = mapped_column(Boolean, default=False)
    reserve_sample_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reserve_sample_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class HoneyBatchDIBRange(UUIDTimeStampedModel):
    __tablename__ = "honey_batch_dib_ranges"

    honey_batch_id: Mapped[str] = mapped_column(
        ForeignKey("honey_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    dib_label_start: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dib_label_end: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    honey_batch: Mapped[HoneyBatch] = relationship(
        "HoneyBatch",
        back_populates="dib_ranges"
    )

