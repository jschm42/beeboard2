from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Dict, Literal, Optional

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

class LLMConfigUpdate(BaseModel):
    chatbot_system_prompt: Optional[str] = None
    draft_system_prompt: Optional[str] = None
    enable_weather_api: Optional[bool] = None
    ai_insights_cron: Optional[str] = None
    kleinunternehmer_regelung: Optional[bool] = None

class LLMConfigOut(LLMConfigBase):
    id: str

    class Config:
        from_attributes = True

class UserAdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserAdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Literal["USER", "SYSTEM_ADMIN"] = "USER"
    is_active: bool = True

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


class SecretSourceStatus(BaseModel):
    db_configured: bool
    env_configured: bool
    effective_source: Optional[Literal["db", "env"]] = None


class ApiKeyConfigOut(BaseModel):
    api_keys: Dict[str, SecretSourceStatus]


class ApiKeyConfigUpdate(BaseModel):
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENWEATHERMAP_API_KEY: Optional[str] = None


class SMTPConfigOut(BaseModel):
    host: Optional[str] = None
    port: int
    from_email: Optional[str] = None
    use_tls: bool
    use_ssl: bool
    username_configured: bool
    password_configured: bool
    db_configured: bool
    env_configured: bool
    effective_source: Optional[Literal["db", "env"]] = None


class SMTPConfigUpdate(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = Field(default=None, ge=1, le=65535)
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[EmailStr] = None
    smtp_use_tls: Optional[bool] = None
    smtp_use_ssl: Optional[bool] = None

