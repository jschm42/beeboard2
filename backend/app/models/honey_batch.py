from __future__ import annotations
from sqlalchemy import String, Date, Float, Boolean, Text, ForeignKey, Integer
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
    bottlings: Mapped[List[HoneyBottling]] = relationship(
        "HoneyBottling",
        back_populates="honey_batch",
        cascade="all, delete-orphan",
        order_by="HoneyBottling.bottling_date.asc(), HoneyBottling.created_at.asc()",
        lazy="joined"
    )

    # Legacy relationship to honey_batch_dib_ranges if present
    dib_ranges: Mapped[List[HoneyBatchDIBRange]] = relationship(
        "HoneyBatchDIBRange",
        back_populates="honey_batch",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    
    @property
    def dib_label_start(self) -> Optional[str]:
        if self.bottlings and self.bottlings[0].dib_ranges:
            return self.bottlings[0].dib_ranges[0].dib_label_start
        return self.dib_ranges[0].dib_label_start if self.dib_ranges else None

    @property
    def dib_label_end(self) -> Optional[str]:
        if self.bottlings and self.bottlings[0].dib_ranges:
            return self.bottlings[0].dib_ranges[0].dib_label_end
        return self.dib_ranges[0].dib_label_end if self.dib_ranges else None
    
    @property
    def total_bottled_kg(self) -> float:
        return sum(b.quantity_kg or 0.0 for b in self.bottlings)

    @property
    def total_bottled_jars(self) -> int:
        return sum(b.quantity_jars or 0 for b in self.bottlings)

    reserve_sample_taken: Mapped[bool] = mapped_column(Boolean, default=False)
    reserve_sample_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reserve_sample_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class HoneyBottling(UUIDTimeStampedModel):
    __tablename__ = "honey_bottlings"

    honey_batch_id: Mapped[str] = mapped_column(
        ForeignKey("honey_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    bottling_date: Mapped[date] = mapped_column(Date)
    jar_size_g: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quantity_jars: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quantity_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    honey_batch: Mapped[HoneyBatch] = relationship(
        "HoneyBatch",
        back_populates="bottlings"
    )
    dib_ranges: Mapped[List[HoneyBottlingDIBRange]] = relationship(
        "HoneyBottlingDIBRange",
        back_populates="bottling",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    @property
    def dib_label_start(self) -> Optional[str]:
        return self.dib_ranges[0].dib_label_start if self.dib_ranges else None

    @property
    def dib_label_end(self) -> Optional[str]:
        return self.dib_ranges[0].dib_label_end if self.dib_ranges else None


class HoneyBottlingDIBRange(UUIDTimeStampedModel):
    __tablename__ = "honey_bottling_dib_ranges"

    bottling_id: Mapped[str] = mapped_column(
        ForeignKey("honey_bottlings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    dib_label_start: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dib_label_end: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    bottling: Mapped[HoneyBottling] = relationship(
        "HoneyBottling",
        back_populates="dib_ranges"
    )


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
