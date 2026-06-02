from __future__ import annotations
from sqlalchemy import String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime

from app.models.base import UUIDTimeStampedModel, CreatedByModel, get_utc_now

class ProductConfig(UUIDTimeStampedModel, CreatedByModel):
    __tablename__ = "product_configs"

    name: Mapped[str] = mapped_column(String(150), index=True)
    honey_type: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    price: Mapped[float] = mapped_column(Float)
    tax_rate: Mapped[float] = mapped_column(Float, default=7.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_batch_selection: Mapped[bool] = mapped_column(Boolean, default=False)
    manage_stock: Mapped[bool] = mapped_column(Boolean, default=False)
    stock: Mapped[float] = mapped_column(Float, default=0.0)
    min_stock: Mapped[float] = mapped_column(Float, default=0.0)

class HoneySale(UUIDTimeStampedModel, CreatedByModel):
    __tablename__ = "honey_sales"

    sale_date: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    product_id: Mapped[str] = mapped_column(ForeignKey("product_configs.id", ondelete="RESTRICT"))
    batch_id: Mapped[Optional[str]] = mapped_column(ForeignKey("honey_batches.id", ondelete="SET NULL"), nullable=True)
    quantity: Mapped[float] = mapped_column(Float)
    total_price: Mapped[float] = mapped_column(Float)
    sales_channel: Mapped[str] = mapped_column(String(50))  # direktverkauf, online, email, verkaufsstand
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    buyer: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # "Verkauft an"

    # Relationships
    product: Mapped[ProductConfig] = relationship("ProductConfig", foreign_keys=[product_id])
    batch: Mapped[Optional[HoneyBatch]] = relationship("HoneyBatch", foreign_keys=[batch_id])
