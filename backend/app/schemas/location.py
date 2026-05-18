from typing import Optional
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

class LocationOut(LocationBase):
    id: str
    apiary_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
