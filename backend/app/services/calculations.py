from datetime import date
from sqlalchemy.orm import Session
from app.models.administration import VarroaMultiplier, FrameType

def detect_season(target_date: date) -> str:
    month = target_date.month
    if month in (3, 4, 5):
        return "SPRING"
    if month in (6, 7, 8):
        return "SUMMER"
    if month in (9, 10, 11):
        return "AUTUMN"
    return "WINTER"

def calculate_inspection_totals(frames, db: Session = None):
    """
    Calculates total brood, food, and bees from list of InspectionFrame models.
    Each frame side has values from 0-8 eighths. We sum these up multiplied by their
    respective FrameType factor.
    """
    brood = 0.0
    food = 0.0
    bees = 0.0

    for frame in frames:
        # Load frame type from frame or inspection detail
        # Note: in Django: frame.inspection.log_entry.hive.frame_type
        # We can either pre-fetch or join. Let's make sure it's accessible.
        # Typically, a frame has an inspection relationship
        inspection = frame.inspection
        log_entry = inspection.log_entry
        hive = log_entry.hive
        frame_type = hive.frame_type
        
        brood += float(frame.brood_eighths or 0) * float(frame_type.brood_multiplier)
        food += float(frame.food_eighths or 0) * float(frame_type.food_multiplier)
        bees += float(frame.bee_eighths or 0) * float(frame_type.bee_multiplier)

    return {
        "brood": brood,
        "food": food,
        "bees": bees,
    }

def estimate_varroa(raw_count: int, target_date: date, db: Session) -> tuple[str, float]:
    season = detect_season(target_date)
    multiplier = db.query(VarroaMultiplier).filter(VarroaMultiplier.season == season).first()
    if multiplier is None:
        return season, float(raw_count)
    return season, float(raw_count) * float(multiplier.multiplier)
