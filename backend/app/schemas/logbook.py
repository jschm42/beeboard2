from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime

class LogSessionBase(BaseModel):
    title: str = Field(..., max_length=30)
    scope_type: str = "APIARY"
    hive_id: Optional[str] = None

class LogSessionCreate(LogSessionBase):
    linked_apiary_ids: List[str] = []
    linked_location_ids: List[str] = []
    linked_hive_ids: List[str] = []

class InspectionBoxBase(BaseModel):
    box_index: int

    # Direct totals per box (Zarge)
    brood_total: int = 0
    food_total: int = 0
    bee_total: int = 0
    drone_total: int = 0
    drone_brood_total: int = 0
    pollen_total: int = 0

    # Optional eighth-based inputs when Achtel-Modus is used
    brood_eighths: Optional[int] = None
    food_eighths: Optional[int] = None
    bee_eighths: Optional[int] = None
    drone_eighths: Optional[int] = None
    drone_brood_eighths: Optional[int] = None
    pollen_eighths: Optional[int] = None


class InspectionBoxCreate(InspectionBoxBase):
    pass


class InspectionBoxOut(InspectionBoxBase):
    id: str
    inspection_id: str

    class Config:
        from_attributes = True


class InspectionDetailCreate(BaseModel):
    boxes: List[InspectionBoxCreate]


class InspectionDetailOut(BaseModel):
    id: str
    log_entry_id: str
    boxes: List[InspectionBoxOut]

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

class LogSessionOut(LogSessionBase):
    id: str
    apiary_id: str
    created_at: datetime
    updated_at: datetime
    linked_apiaries: List[LogEntryApiaryOut] = []
    linked_locations: List[LogEntryLocationOut] = []
    linked_hives: List[LogEntryHiveOut] = []

    class Config:
        from_attributes = True
