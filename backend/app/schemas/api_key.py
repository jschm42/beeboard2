from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ApiKeyCreate(BaseModel):
    name: str
    expires_days: Optional[int] = None

class ApiKeyOut(BaseModel):
    id: str
    name: str
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyCreateResponse(BaseModel):
    api_key_info: ApiKeyOut
    raw_key: str
