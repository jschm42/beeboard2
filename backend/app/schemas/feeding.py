from pydantic import BaseModel, ConfigDict
from datetime import date as dt_date, datetime
from typing import Optional, List, Dict, Any


class FeedTypeBase(BaseModel):
    name: str
    unit: str = "kg"
    is_active: bool = True
    description: Optional[str] = None


class FeedTypeCreate(FeedTypeBase):
    pass


class FeedTypeUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class FeedTypeOut(FeedTypeBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class LocationSimpleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class HiveSimpleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    location_id: str
    location: Optional[LocationSimpleOut] = None


class FeedingBase(BaseModel):
    hive_id: str
    feed_type_id: str
    date: dt_date
    amount: float
    fed_by: Optional[str] = None
    notes: Optional[str] = None


class FeedingCreate(FeedingBase):
    pass


class FeedingBatchCreate(BaseModel):
    hive_ids: List[str]
    feed_type_id: str
    date: dt_date
    amount: float
    fed_by: Optional[str] = None
    notes: Optional[str] = None


class FeedingUpdate(BaseModel):
    hive_id: Optional[str] = None
    feed_type_id: Optional[str] = None
    date: Optional[dt_date] = None
    amount: Optional[float] = None
    fed_by: Optional[str] = None
    notes: Optional[str] = None


class FeedingOut(FeedingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    apiary_id: str
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    hive: HiveSimpleOut
    feed_type: FeedTypeOut


class FeedingTypeTotal(BaseModel):
    feed_type_id: str
    feed_type_name: str
    unit: str
    total_amount: float
    count: int


class FeedingStatsSummary(BaseModel):
    total_count: int
    totals_by_unit: Dict[str, float]
    by_feed_type: List[FeedingTypeTotal]
