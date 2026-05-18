from __future__ import annotations
from sqlalchemy import String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.models.base import UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel

class Location(UUIDTimeStampedModel, CreatedByModel, ApiaryScopedModel):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(120), index=True)
    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    hives: Mapped[List["Hive"]] = relationship("Hive", back_populates="location")
