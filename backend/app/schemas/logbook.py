from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime

class LogSessionBase(BaseModel):
    title: str = Field(..., max_length=30)
    hive_id: Optional[str] = None

class LogSessionCreate(LogSessionBase):
    pass

class LogSessionOut(LogSessionBase):
    id: str
    apiary_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InspectionFrameBase(BaseModel):
    frame_number: int
    side: int  # 1 or 2
    brood_eighths: int
    food_eighths: int
    bee_eighths: int
    drone_eighths: int = 0
    drone_brood_eighths: int = 0
    pollen_eighths: int = 0
    brood_multiplier: Optional[float] = 1.0
    food_multiplier: Optional[float] = 1.0
    bee_multiplier: Optional[float] = 1.0
    drone_multiplier: Optional[float] = 1.0
    drone_brood_multiplier: Optional[float] = 1.0
    pollen_multiplier: Optional[float] = 1.0

class InspectionFrameCreate(InspectionFrameBase):
    pass

class InspectionFrameOut(InspectionFrameBase):
    id: str
    inspection_id: str

    class Config:
        from_attributes = True

class InspectionDetailCreate(BaseModel):
    frames: List[InspectionFrameCreate]

class InspectionDetailOut(BaseModel):
    id: str
    log_entry_id: str
    frames: List[InspectionFrameOut]

    class Config:
        from_attributes = True

class VarroaCountDetailCreate(BaseModel):
    raw_count: int

class VarroaCountDetailOut(BaseModel):
    id: str
    log_entry_id: str
    raw_count: int
    season: str
    estimated_total: float

    class Config:
        from_attributes = True

class VarroaTreatmentDetailCreate(BaseModel):
    product: str
    dosage: str = ""
    treatment_notes: Optional[str] = ""

class VarroaTreatmentDetailOut(BaseModel):
    id: str
    log_entry_id: str
    product: str
    dosage: str
    treatment_notes: Optional[str] = ""

    class Config:
        from_attributes = True

class LogEntryImageOut(BaseModel):
    id: str
    log_entry_id: str
    image_path: str
    thumbnail_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class LogEntryBase(BaseModel):
    hive_id: str
    session_id: Optional[str] = None
    date: date
    entry_type: str  # INSPECTION, VARROA_COUNT, VARROA_TREATMENT, GENERAL
    notes: Optional[str] = None

class LogEntryCreate(LogEntryBase):
    inspection_detail: Optional[InspectionDetailCreate] = None
    varroa_count_detail: Optional[VarroaCountDetailCreate] = None
    varroa_treatment_detail: Optional[VarroaTreatmentDetailCreate] = None

class LogEntryUserOut(BaseModel):
    id: str
    username: str

    class Config:
        from_attributes = True

class LogEntryApiaryOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class LogEntryLocationOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class LogEntryHiveOut(BaseModel):
    id: str
    name: str
    location: Optional[LogEntryLocationOut] = None

    class Config:
        from_attributes = True

class LogEntryOut(LogEntryBase):
    id: str
    apiary_id: str
    created_by_id: Optional[str] = None
    created_by: Optional[LogEntryUserOut] = None
    apiary: Optional[LogEntryApiaryOut] = None
    hive: Optional[LogEntryHiveOut] = None
    inspection_detail: Optional[InspectionDetailOut] = None
    varroa_count_detail: Optional[VarroaCountDetailOut] = None
    varroa_treatment_detail: Optional[VarroaTreatmentDetailOut] = None
    images: List[LogEntryImageOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
