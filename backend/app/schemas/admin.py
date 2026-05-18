from pydantic import BaseModel
from datetime import datetime

class FrameTypeBase(BaseModel):
    name: str
    is_default: bool = False
    brood_multiplier: float = 1.0
    food_multiplier: float = 1.0
    bee_multiplier: float = 1.0

class FrameTypeCreate(FrameTypeBase):
    pass

class FrameTypeOut(FrameTypeBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class VarroaMultiplierBase(BaseModel):
    season: str
    multiplier: float

class VarroaMultiplierOut(VarroaMultiplierBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
