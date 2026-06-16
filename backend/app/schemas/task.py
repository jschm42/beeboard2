from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime

class TaskLocationOut(BaseModel):
    id: str
    name: str
    address: str

    class Config:
        from_attributes = True

class TaskHiveOut(BaseModel):
    id: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    location_id: Optional[str] = None
    hive_id: Optional[str] = None
    is_recurring: bool = False
    recurrence_interval: Optional[str] = None  # DAILY, WEEKLY, BIWEEKLY, MONTHLY, YEARLY, EVERY_N_DAYS

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    location_id: Optional[str] = None
    hive_id: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_interval: Optional[str] = None  # DAILY, WEEKLY, BIWEEKLY, MONTHLY, YEARLY, EVERY_N_DAYS
    is_completed: Optional[bool] = None

class TaskOut(TaskBase):
    id: str
    apiary_id: str
    created_by_id: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    location: Optional[TaskLocationOut] = None
    hive: Optional[TaskHiveOut] = None

    class Config:
        from_attributes = True
