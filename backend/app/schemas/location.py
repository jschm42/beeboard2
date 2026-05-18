from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class LocationBase(BaseModel):
    name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationHiveOut(BaseModel):
    id: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class LocationOut(LocationBase):
    id: str
    apiary_id: str
    hives: List[LocationHiveOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
