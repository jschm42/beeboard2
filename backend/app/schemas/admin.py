from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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

class LLMConfigBase(BaseModel):
    chatbot_system_prompt: str
    draft_system_prompt: str
    enable_weather_api: bool

class LLMConfigUpdate(BaseModel):
    chatbot_system_prompt: Optional[str] = None
    draft_system_prompt: Optional[str] = None
    enable_weather_api: Optional[bool] = None

class LLMConfigOut(LLMConfigBase):
    id: str

    class Config:
        from_attributes = True

class UserAdminUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
