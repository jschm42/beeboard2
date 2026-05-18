from __future__ import annotations
from sqlalchemy import String, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.models.base import UUIDTimeStampedModel

class Apiary(UUIDTimeStampedModel):
    __tablename__ = "apiaries"

    name: Mapped[str] = mapped_column(String(120), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    memberships: Mapped[List["ApiaryMembership"]] = relationship(
        "ApiaryMembership",
        back_populates="apiary",
        cascade="all, delete-orphan"
    )
    ai_insights: Mapped[List["AIInsight"]] = relationship(
        "AIInsight",
        back_populates="apiary",
        cascade="all, delete-orphan",
        order_by="desc(AIInsight.created_at)"
    )

class ApiaryMembership(UUIDTimeStampedModel):
    __tablename__ = "apiary_memberships"

    apiary_id: Mapped[str] = mapped_column(ForeignKey("apiaries.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20), default="USER")  # ADMIN, USER

    # Relationships
    apiary: Mapped["Apiary"] = relationship("Apiary", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="apiary_memberships")

    __table_args__ = (
        UniqueConstraint("apiary_id", "user_id", name="uq_apiary_user"),
    )
