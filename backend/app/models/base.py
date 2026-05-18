from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, relationship
from app.core.database import Base

def get_utc_now():
    return datetime.now(timezone.utc)

class UUIDTimeStampedModel(Base):
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=get_utc_now, 
        onupdate=get_utc_now
    )

class CreatedByModel:
    @declared_attr
    def created_by_id(cls) -> Mapped[Optional[str]]:
        return mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
        
    @declared_attr
    def created_by(cls):
        from app.models.user import User
        return relationship("User", foreign_keys=[cls.created_by_id])

class ApiaryScopedModel:
    @declared_attr
    def apiary_id(cls) -> Mapped[Optional[str]]:
        return mapped_column(ForeignKey("apiaries.id", ondelete="CASCADE"), nullable=True)

    @declared_attr
    def apiary(cls):
        from app.models.apiary import Apiary
        return relationship("Apiary", foreign_keys=[cls.apiary_id])
