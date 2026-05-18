from sqlalchemy import String, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDTimeStampedModel

class FrameType(UUIDTimeStampedModel):
    __tablename__ = "frame_types"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    brood_multiplier: Mapped[float] = mapped_column(Float, default=1.00)
    food_multiplier: Mapped[float] = mapped_column(Float, default=1.00)
    bee_multiplier: Mapped[float] = mapped_column(Float, default=1.00)

class VarroaMultiplier(UUIDTimeStampedModel):
    __tablename__ = "varroa_multipliers"

    season: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # SPRING, SUMMER, AUTUMN, WINTER
    multiplier: Mapped[float] = mapped_column(Float)
