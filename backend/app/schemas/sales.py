from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.honey import HoneyBatchOut

class ProductConfigBase(BaseModel):
    name: str
    honey_type: Optional[str] = None
    price: float
    tax_rate: float
    is_active: bool = True
    requires_batch_selection: bool = False

class ProductConfigCreate(ProductConfigBase):
    pass

class ProductConfigUpdate(BaseModel):
    name: Optional[str] = None
    honey_type: Optional[str] = None
    price: Optional[float] = None
    tax_rate: Optional[float] = None
    is_active: Optional[bool] = None
    requires_batch_selection: Optional[bool] = None

class ProductConfigOut(ProductConfigBase):
    id: str
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HoneySaleBase(BaseModel):
    sale_date: datetime
    product_id: str
    batch_id: Optional[str] = None
    quantity: float
    total_price: float
    sales_channel: str
    notes: Optional[str] = None
    buyer: Optional[str] = None

class HoneySaleCreate(BaseModel):
    sale_date: Optional[datetime] = None
    product_id: str
    batch_id: Optional[str] = None
    quantity: float
    total_price: Optional[float] = None  # If not provided, computed on creation
    sales_channel: str
    notes: Optional[str] = None
    buyer: Optional[str] = None

class HoneySaleUpdate(BaseModel):
    sale_date: Optional[datetime] = None
    product_id: Optional[str] = None
    batch_id: Optional[str] = None
    quantity: Optional[float] = None
    total_price: Optional[float] = None
    sales_channel: Optional[str] = None
    notes: Optional[str] = None
    buyer: Optional[str] = None

class HoneySaleOut(HoneySaleBase):
    id: str
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductConfigOut] = None
    batch: Optional[HoneyBatchOut] = None

    class Config:
        from_attributes = True
