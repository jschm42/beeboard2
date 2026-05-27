from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FrameTypeBase(BaseModel):
    name: str
    is_default: bool = False
    brood_multiplier: float = 1.0
    food_multiplier: float = 1.0
    bee_multiplier: float = 1.0
    drone_multiplier: float = 1.0
    drone_brood_multiplier: float = 1.0
    pollen_multiplier: float = 1.0

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
    ai_insights_cron: Optional[str] = None
    kleinunternehmer_regelung: bool = False
    calculate_taxes: bool = True
    currency: str = "EUR"
    tax_rates: str = "0.0,7.0,19.0"

class LLMConfigUpdate(BaseModel):
    chatbot_system_prompt: Optional[str] = None
    draft_system_prompt: Optional[str] = None
    enable_weather_api: Optional[bool] = None
    ai_insights_cron: Optional[str] = None
    kleinunternehmer_regelung: Optional[bool] = None
    calculate_taxes: Optional[bool] = None
    currency: Optional[str] = None
    tax_rates: Optional[str] = None


class LLMConfigOut(LLMConfigBase):
    id: str

    class Config:
        from_attributes = True

class UserAdminUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

class NumberRangeBase(BaseModel):
    name: str
    prefix: Optional[str] = None
    current_value: int
    digits: int
    is_active: bool = True

class NumberRangeUpdate(BaseModel):
    name: Optional[str] = None
    prefix: Optional[str] = None
    current_value: Optional[int] = None
    digits: Optional[int] = None
    is_active: Optional[bool] = None

class NumberRangeOut(NumberRangeBase):
    id: str
    key: str
    created_at: datetime

    class Config:
        from_attributes = True


class AIInsightCronJobBase(BaseModel):
    name: str
    prompt: str
    cron_expression: str
    inject_weather: bool = False
    inject_locations: bool = True
    inject_apiary: bool = True
    inject_hives: bool = True
    inject_log_entries: bool = True
    log_scope: str = "IMKEREI"
    max_log_entries: int = 20
    is_active: bool = True


class AIInsightCronJobCreate(AIInsightCronJobBase):
    pass


class AIInsightCronJobUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    cron_expression: Optional[str] = None
    inject_weather: Optional[bool] = None
    inject_locations: Optional[bool] = None
    inject_apiary: Optional[bool] = None
    inject_hives: Optional[bool] = None
    inject_log_entries: Optional[bool] = None
    log_scope: Optional[str] = None
    max_log_entries: Optional[int] = None
    is_active: Optional[bool] = None


class AIInsightCronJobOut(AIInsightCronJobBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

