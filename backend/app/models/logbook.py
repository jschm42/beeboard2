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
    frames: Mapped[List["InspectionFrame"]] = relationship(
        "InspectionFrame",
        back_populates="inspection",
        cascade="all, delete-orphan"
    )

class InspectionFrame(UUIDTimeStampedModel):
    __tablename__ = "inspection_frames"

    inspection_id: Mapped[str] = mapped_column(ForeignKey("inspection_details.id", ondelete="CASCADE"))
    frame_number: Mapped[int] = mapped_column(Integer)
    side: Mapped[int] = mapped_column(Integer)  # 1 or 2
    brood_eighths: Mapped[int] = mapped_column(Integer, default=0)
    food_eighths: Mapped[int] = mapped_column(Integer, default=0)
    bee_eighths: Mapped[int] = mapped_column(Integer, default=0)
    drone_eighths: Mapped[int] = mapped_column(Integer, default=0)
    drone_brood_eighths: Mapped[int] = mapped_column(Integer, default=0)
    pollen_eighths: Mapped[int] = mapped_column(Integer, default=0)

    # Snapshotted multipliers for biology statistics resilience
    brood_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    food_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    bee_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    drone_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    drone_brood_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    pollen_multiplier: Mapped[float] = mapped_column(Float, default=1.0)

    # Relationships
    inspection: Mapped["InspectionDetail"] = relationship("InspectionDetail", back_populates="frames")

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
