from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut

class ApiaryBase(BaseModel):
    name: str
    notes: Optional[str] = None

class ApiaryCreate(ApiaryBase):
    pass

class ApiaryOut(ApiaryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApiaryMembershipBase(BaseModel):
    apiary_id: str
    user_id: str
    role: str = "USER"

class ApiaryMembershipCreate(BaseModel):
    username_or_email: str
    role: str = "USER"

class ApiaryMembershipOut(BaseModel):
    id: str
    apiary_id: str
    user_id: str
    role: str
    user: UserOut
    created_at: datetime

    class Config:
        from_attributes = True
