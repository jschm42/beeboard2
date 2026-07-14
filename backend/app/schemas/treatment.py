from pydantic import BaseModel
from datetime import date as dt_date, datetime
from typing import Optional, List

class TreatmentMethodBase(BaseModel):
    name: str
    unit: str = "ml"
    is_active: bool = True

class TreatmentMethodCreate(TreatmentMethodBase):
    pass

class TreatmentMethodOut(TreatmentMethodBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class TreatmentApplicationTypeBase(BaseModel):
    name: str
    is_active: bool = True

class TreatmentApplicationTypeCreate(TreatmentApplicationTypeBase):
    pass

class TreatmentApplicationTypeOut(TreatmentApplicationTypeBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class TreatmentImageOut(BaseModel):
    id: str
    image_path: str
    thumbnail_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TreatmentBase(BaseModel):
    hive_id: str
    treatment_method_id: str
    application_type_id: Optional[str] = None
    date: dt_date
    amount: float
    notes: Optional[str] = None

class TreatmentCreate(TreatmentBase):
    pass

class TreatmentUpdate(BaseModel):
    hive_id: Optional[str] = None
    treatment_method_id: Optional[str] = None
    application_type_id: Optional[str] = None
    date: Optional[dt_date] = None
    amount: Optional[float] = None
    notes: Optional[str] = None

class LocationSimpleOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class HiveSimpleOut(BaseModel):
    id: str
    name: str
    location_id: str
    location: Optional[LocationSimpleOut] = None

    class Config:
        from_attributes = True

class TreatmentOut(TreatmentBase):
    id: str
    apiary_id: str
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    treatment_method: TreatmentMethodOut
    application_type: Optional[TreatmentApplicationTypeOut] = None
    hive: HiveSimpleOut
    images: List[TreatmentImageOut] = []

    class Config:
        from_attributes = True
