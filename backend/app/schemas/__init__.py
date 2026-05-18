from app.schemas.user import UserBase, UserCreate, UserUpdate, UserOut, Token, TokenPayload
from app.schemas.apiary import ApiaryBase, ApiaryCreate, ApiaryOut, ApiaryMembershipBase, ApiaryMembershipCreate, ApiaryMembershipOut
from app.schemas.location import LocationBase, LocationCreate, LocationOut
from app.schemas.admin import FrameTypeBase, FrameTypeCreate, FrameTypeOut, VarroaMultiplierBase, VarroaMultiplierOut
from app.schemas.hive import HiveBoxBase, HiveBoxCreate, HiveBoxOut, HiveBase, HiveCreate, HiveOut
from app.schemas.logbook import (
    LogSessionBase, LogSessionCreate, LogSessionOut,
    InspectionFrameBase, InspectionFrameCreate, InspectionFrameOut,
    InspectionDetailCreate, InspectionDetailOut,
    VarroaCountDetailCreate, VarroaCountDetailOut,
    VarroaTreatmentDetailCreate, VarroaTreatmentDetailOut,
    LogEntryImageOut, LogEntryBase, LogEntryCreate, LogEntryOut
)
from app.schemas.ai import AIChatQuery, AIChatResponse, AIDraftQuery, AIDraftResponse

# Export all schemas
__all__ = [
    "UserBase", "UserCreate", "UserUpdate", "UserOut", "Token", "TokenPayload",
    "ApiaryBase", "ApiaryCreate", "ApiaryOut", "ApiaryMembershipBase", "ApiaryMembershipCreate", "ApiaryMembershipOut",
    "LocationBase", "LocationCreate", "LocationOut",
    "FrameTypeBase", "FrameTypeCreate", "FrameTypeOut", "VarroaMultiplierBase", "VarroaMultiplierOut",
    "HiveBoxBase", "HiveBoxCreate", "HiveBoxOut", "HiveBase", "HiveCreate", "HiveOut",
    "LogSessionBase", "LogSessionCreate", "LogSessionOut",
    "InspectionFrameBase", "InspectionFrameCreate", "InspectionFrameOut",
    "InspectionDetailCreate", "InspectionDetailOut",
    "VarroaCountDetailCreate", "VarroaCountDetailOut",
    "VarroaTreatmentDetailCreate", "VarroaTreatmentDetailOut",
    "LogEntryImageOut", "LogEntryBase", "LogEntryCreate", "LogEntryOut",
    "AIChatQuery", "AIChatResponse", "AIDraftQuery", "AIDraftResponse"
]
