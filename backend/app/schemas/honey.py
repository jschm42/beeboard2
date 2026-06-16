from typing import Optional, List
from pydantic import BaseModel, model_validator
from datetime import date, datetime
from app.schemas.user import UserOut

class HoneyBatchDIBRangeBase(BaseModel):
    dib_label_start: Optional[str] = None
    dib_label_end: Optional[str] = None

class HoneyBatchDIBRangeCreate(HoneyBatchDIBRangeBase):
    pass

class HoneyBatchDIBRangeOut(HoneyBatchDIBRangeBase):
    id: str
    class Config:
        from_attributes = True

class HoneyBatchBase(BaseModel):
    batch_number: Optional[str] = None
    honey_type: str
    harvest_date: date
    bottling_date: Optional[date] = None
    quantity_kg: float
    water_content_percent: Optional[float] = None
    heating_temperature_celsius: Optional[float] = None
    best_before_date: date
    is_exact_date: bool = False
    dib_label_start: Optional[str] = None
    dib_label_end: Optional[str] = None
    dib_ranges: List[HoneyBatchDIBRangeOut] = []
    reserve_sample_taken: bool = False
    reserve_sample_date: Optional[date] = None
    reserve_sample_id: Optional[str] = None
    notes: Optional[str] = None

class HoneyBatchCreate(HoneyBatchBase):
    dib_ranges: Optional[List[HoneyBatchDIBRangeCreate]] = None

    @model_validator(mode='after')
    def validate_batch_number(self):
        if not self.is_exact_date and (not self.batch_number or not self.batch_number.strip()):
            raise ValueError("Die Los-Nr. (batch_number) ist zwingend erforderlich, wenn das MHD nicht taggenau (is_exact_date=True) angegeben ist.")
        return self

class HoneyBatchUpdate(BaseModel):
    batch_number: Optional[str] = None
    honey_type: Optional[str] = None
    harvest_date: Optional[date] = None
    bottling_date: Optional[date] = None
    quantity_kg: Optional[float] = None
    water_content_percent: Optional[float] = None
    heating_temperature_celsius: Optional[float] = None
    best_before_date: Optional[date] = None
    is_exact_date: Optional[bool] = None
    dib_label_start: Optional[str] = None
    dib_label_end: Optional[str] = None
    dib_ranges: Optional[List[HoneyBatchDIBRangeCreate]] = None
    reserve_sample_taken: Optional[bool] = None
    reserve_sample_date: Optional[date] = None
    reserve_sample_id: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode='after')
    def validate_batch_number(self):
        # We only validate if is_exact_date is explicitly set or defaulted, and we check the batch number
        if self.is_exact_date is False and (not self.batch_number or not self.batch_number.strip()):
            raise ValueError("Die Los-Nr. (batch_number) ist zwingend erforderlich, wenn das MHD nicht taggenau angegeben ist.")
        return self

class HoneyBatchOut(HoneyBatchBase):
    id: str
    apiary_id: str
    created_by_id: Optional[str] = None
    created_by: Optional[UserOut] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

