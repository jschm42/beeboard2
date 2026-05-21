from __future__ import annotations
from sqlalchemy import String, ForeignKey, Integer, Float, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from typing import List, Optional

from app.models.base import UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel

class LogSession(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "log_sessions"

    title: Mapped[str] = mapped_column(String(160))
    hive_id: Mapped[Optional[str]] = mapped_column(ForeignKey("hives.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    hive: Mapped["Hive"] = relationship("Hive", foreign_keys=[hive_id])
    entries: Mapped[List["LogEntry"]] = relationship(
        "LogEntry",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="LogEntry.date.desc()"
    )

class LogEntry(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "log_entries"

    hive_id: Mapped[str] = mapped_column(ForeignKey("hives.id", ondelete="CASCADE"))
    session_id: Mapped[Optional[str]] = mapped_column(ForeignKey("log_sessions.id", ondelete="CASCADE"), nullable=True)
    date: Mapped[date] = mapped_column(Date)
    entry_type: Mapped[str] = mapped_column(String(30))  # INSPECTION, VARROA_COUNT, VARROA_TREATMENT, GENERAL
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    hive: Mapped["Hive"] = relationship("Hive", back_populates="log_entries", foreign_keys=[hive_id])
    session: Mapped["LogSession"] = relationship("LogSession", back_populates="entries", foreign_keys=[session_id])
    
    inspection_detail: Mapped["InspectionDetail"] = relationship(
        "InspectionDetail",
        back_populates="log_entry",
        cascade="all, delete-orphan",
        uselist=False
    )
    varroa_count_detail: Mapped["VarroaCountDetail"] = relationship(
        "VarroaCountDetail",
        back_populates="log_entry",
        cascade="all, delete-orphan",
        uselist=False
    )
    varroa_treatment_detail: Mapped["VarroaTreatmentDetail"] = relationship(
        "VarroaTreatmentDetail",
        back_populates="log_entry",
        cascade="all, delete-orphan",
        uselist=False
    )
    images: Mapped[List["LogEntryImage"]] = relationship(
        "LogEntryImage",
        back_populates="log_entry",
        cascade="all, delete-orphan"
    )

class InspectionDetail(UUIDTimeStampedModel):
    __tablename__ = "inspection_details"

    log_entry_id: Mapped[str] = mapped_column(ForeignKey("log_entries.id", ondelete="CASCADE"), unique=True)

    # Relationships
    log_entry: Mapped["LogEntry"] = relationship("LogEntry", back_populates="inspection_detail")
    # New simplified box-based inspection model
    boxes: Mapped[List["InspectionBox"]] = relationship(
        "InspectionBox",
        back_populates="inspection",
        cascade="all, delete-orphan"
    )

class InspectionBox(UUIDTimeStampedModel):
    """Simplified box-based inspection snapshot.

    Stores direct totals per box (Zarge) plus optional eighth-based inputs
    when the user worked in Achtel-Modus.
    """

    __tablename__ = "inspection_boxes"

    inspection_id: Mapped[str] = mapped_column(ForeignKey("inspection_details.id", ondelete="CASCADE"))

    # Index of the box within the hive (0,1,2,...) – UI order
    box_index: Mapped[int] = mapped_column(Integer)

    # Direct totals (exact/estimated quantities)
    brood_total: Mapped[int] = mapped_column(Integer, default=0)
    food_total: Mapped[int] = mapped_column(Integer, default=0)
    bee_total: Mapped[int] = mapped_column(Integer, default=0)
    drone_total: Mapped[int] = mapped_column(Integer, default=0)
    drone_brood_total: Mapped[int] = mapped_column(Integer, default=0)
    pollen_total: Mapped[int] = mapped_column(Integer, default=0)

    # Optional eighth-based inputs (0–8 per box) when Achtel-Modus is used
    brood_eighths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    food_eighths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bee_eighths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    drone_eighths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    drone_brood_eighths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pollen_eighths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    inspection: Mapped["InspectionDetail"] = relationship("InspectionDetail", back_populates="boxes")

class VarroaCountDetail(UUIDTimeStampedModel):
    __tablename__ = "varroa_count_details"

    log_entry_id: Mapped[str] = mapped_column(ForeignKey("log_entries.id", ondelete="CASCADE"), unique=True)
    raw_count: Mapped[int] = mapped_column(Integer)
    season: Mapped[str] = mapped_column(String(20))  # SPRING, SUMMER, AUTUMN, WINTER
    estimated_total: Mapped[float] = mapped_column(Float)

    # Relationships
    log_entry: Mapped["LogEntry"] = relationship("LogEntry", back_populates="varroa_count_detail")

class VarroaTreatmentDetail(UUIDTimeStampedModel):
    __tablename__ = "varroa_treatment_details"

    log_entry_id: Mapped[str] = mapped_column(ForeignKey("log_entries.id", ondelete="CASCADE"), unique=True)
    product: Mapped[str] = mapped_column(String(120))
    dosage: Mapped[str] = mapped_column(String(120), default="")
    treatment_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")

    # Relationships
    log_entry: Mapped["LogEntry"] = relationship("LogEntry", back_populates="varroa_treatment_detail")

class LogEntryImage(UUIDTimeStampedModel):
    __tablename__ = "log_entry_images"

    log_entry_id: Mapped[str] = mapped_column(ForeignKey("log_entries.id", ondelete="CASCADE"))
    image_path: Mapped[str] = mapped_column(String(255))
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    log_entry: Mapped["LogEntry"] = relationship("LogEntry", back_populates="images")
