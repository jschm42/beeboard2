from __future__ import annotations
from sqlalchemy import String, ForeignKey, Float, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from typing import List, Optional

from app.models.base import UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel

class TreatmentMethod(UUIDTimeStampedModel):
    __tablename__ = "treatment_methods"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(20), default="ml")
    is_active: Mapped[bool] = mapped_column(default=True)
    manufacturer_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    attachments: Mapped[List["TreatmentMethodAttachment"]] = relationship(
        "TreatmentMethodAttachment",
        back_populates="treatment_method",
        cascade="all, delete-orphan",
        order_by="TreatmentMethodAttachment.created_at"
    )

class TreatmentMethodAttachment(UUIDTimeStampedModel):
    __tablename__ = "treatment_method_attachments"

    treatment_method_id: Mapped[str] = mapped_column(ForeignKey("treatment_methods.id", ondelete="CASCADE"), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Relationships
    treatment_method: Mapped["TreatmentMethod"] = relationship("TreatmentMethod", back_populates="attachments")

class TreatmentApplicationType(UUIDTimeStampedModel):
    __tablename__ = "treatment_application_types"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)

class Treatment(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "treatments"

    hive_id: Mapped[str] = mapped_column(ForeignKey("hives.id", ondelete="CASCADE"), index=True)
    treatment_method_id: Mapped[str] = mapped_column(ForeignKey("treatment_methods.id", ondelete="RESTRICT"), index=True)
    application_type_id: Mapped[Optional[str]] = mapped_column(ForeignKey("treatment_application_types.id", ondelete="SET NULL"), nullable=True, index=True)
    date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    treated_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    hive: Mapped["Hive"] = relationship("Hive", back_populates="treatments", foreign_keys=[hive_id])
    treatment_method: Mapped["TreatmentMethod"] = relationship("TreatmentMethod")
    application_type: Mapped[Optional["TreatmentApplicationType"]] = relationship("TreatmentApplicationType")
    images: Mapped[List["TreatmentImage"]] = relationship(
        "TreatmentImage",
        back_populates="treatment",
        cascade="all, delete-orphan"
    )

class TreatmentImage(UUIDTimeStampedModel):
    __tablename__ = "treatment_images"

    treatment_id: Mapped[str] = mapped_column(ForeignKey("treatments.id", ondelete="CASCADE"), index=True)
    image_path: Mapped[str] = mapped_column(String(255))
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    treatment: Mapped["Treatment"] = relationship("Treatment", back_populates="images")
