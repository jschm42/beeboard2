from __future__ import annotations
from sqlalchemy import String, ForeignKey, Integer, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.models.base import UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel

class Hive(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "hives"

    name: Mapped[str] = mapped_column(String(50), index=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id", ondelete="RESTRICT"))
    frame_type_id: Mapped[str] = mapped_column(ForeignKey("frame_types.id", ondelete="RESTRICT"))
    queen_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    location: Mapped["Location"] = relationship("Location", back_populates="hives")
    frame_type: Mapped["FrameType"] = relationship("FrameType", foreign_keys=[frame_type_id])
    boxes: Mapped[List["HiveBox"]] = relationship(
        "HiveBox",
        back_populates="hive",
        cascade="all, delete-orphan",
        order_by="HiveBox.order"
    )
    log_entries: Mapped[List["LogEntry"]] = relationship(
        "LogEntry",
        back_populates="hive",
        cascade="all, delete-orphan"
    )
    treatments: Mapped[List["Treatment"]] = relationship(
        "Treatment",
        back_populates="hive",
        cascade="all, delete-orphan"
    )

class HiveBox(UUIDTimeStampedModel):
    __tablename__ = "hive_boxes"

    hive_id: Mapped[str] = mapped_column(ForeignKey("hives.id", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer, default=1)
    frame_type_id: Mapped[str] = mapped_column(ForeignKey("frame_types.id", ondelete="RESTRICT"))
    frame_count: Mapped[int] = mapped_column(Integer)
    box_type: Mapped[str] = mapped_column(String(12))  # BROOD, HONEY

    # Relationships
    hive: Mapped["Hive"] = relationship("Hive", back_populates="boxes")
    frame_type: Mapped["FrameType"] = relationship("FrameType", foreign_keys=[frame_type_id])

    __table_args__ = (
        UniqueConstraint("hive_id", "order", name="uq_hive_box_order"),
    )
