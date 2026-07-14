from app.core.database import Base
from app.models.user import User
from app.models.apiary import Apiary, ApiaryMembership
from app.models.location import Location
from app.models.administration import FrameType, VarroaMultiplier, LLMConfig, NumberRange
from app.models.hive import Hive, HiveBox
from app.models.logbook import (
    LogSession, 
    LogEntry, 
    InspectionDetail, 
    InspectionBox,
    VarroaCountDetail, 
    VarroaTreatmentDetail, 
    LogEntryImage
)
from app.models.ai_insight import AIInsight, AIInsightCronJob
from app.models.honey_batch import HoneyBatch, HoneyBatchDIBRange
from app.models.sales import ProductConfig, HoneySale
from app.models.task import Task
from app.models.bee_agent import BeeAgentJob, BeeAgentProposal
from app.models.treatment import TreatmentMethod, Treatment, TreatmentImage, TreatmentApplicationType

# Export all models for easier importing
__all__ = [
    "Base",
    "User",
    "Apiary",
    "ApiaryMembership",
    "Location",
    "FrameType",
    "VarroaMultiplier",
    "LLMConfig",
    "NumberRange",
    "Hive",
    "HiveBox",
    "LogSession",
    "LogEntry",
    "InspectionDetail",
    "InspectionBox",
    "VarroaCountDetail",
    "VarroaTreatmentDetail",
    "LogEntryImage",
    "AIInsight",
    "AIInsightCronJob",
    "HoneyBatch",
    "HoneyBatchDIBRange",
    "ProductConfig",
    "HoneySale",
    "Task",
    "BeeAgentJob",
    "BeeAgentProposal",
    "TreatmentMethod",
    "Treatment",
    "TreatmentImage",
    "TreatmentApplicationType",
]
