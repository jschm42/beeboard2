from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from app.schemas.admin import FrameTypeOut
from app.schemas.location import LocationOut

class HiveBoxBase(BaseModel):
    order: int
    frame_type_id: str
    frame_count: int
    box_type: str  # BROOD, HONEY

class HiveBoxCreate(HiveBoxBase):
    pass

class HiveBoxOut(HiveBoxBase):
    id: str
    hive_id: str
    frame_type: FrameTypeOut
    created_at: datetime

    class Config:
        from_attributes = True

class HiveBase(BaseModel):
    name: str
    location_id: str
    frame_type_id: str
    queen_year: Optional[int] = None
    is_active: bool = True
    notes: Optional[str] = None

class HiveCreate(HiveBase):
    boxes: List[HiveBoxCreate] = []

class HiveOut(HiveBase):
    id: str
    apiary_id: str
    image_path: Optional[str] = None
    frame_type: FrameTypeOut
    location: LocationOut
    boxes: List[HiveBoxOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
