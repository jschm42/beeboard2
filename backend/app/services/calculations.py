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
    Calculates total brood, food, bees, drones, drone brood, and pollen from list of InspectionFrame models.
    Each frame side has values from 0-8 eighths. We sum these up multiplied by their
    respective FrameType factor.
    """
    brood = 0.0
    food = 0.0
    bees = 0.0
    drones = 0.0
    drone_brood = 0.0
    pollen = 0.0

    for frame in frames:
        # Check if multipliers are snapshotted on the frame
        if getattr(frame, "brood_multiplier", None) is not None:
            b_mult = float(frame.brood_multiplier)
            f_mult = float(frame.food_multiplier)
            bee_mult = float(frame.bee_multiplier)
            dr_mult = float(frame.drone_multiplier or 1.0)
            dr_b_mult = float(frame.drone_brood_multiplier or 1.0)
            p_mult = float(frame.pollen_multiplier or 1.0)
        else:
            # Backwards compatibility / Unit test fallback
            inspection = frame.inspection
            log_entry = inspection.log_entry
            hive = log_entry.hive
            frame_type = hive.frame_type
            b_mult = float(frame_type.brood_multiplier)
            f_mult = float(frame_type.food_multiplier)
            bee_mult = float(frame_type.bee_multiplier)
            dr_mult = float(frame_type.drone_multiplier or 1.0)
            dr_b_mult = float(frame_type.drone_brood_multiplier or 1.0)
            p_mult = float(frame_type.pollen_multiplier or 1.0)
        
        brood += float(frame.brood_eighths or 0) * b_mult
        food += float(frame.food_eighths or 0) * f_mult
        bees += float(frame.bee_eighths or 0) * bee_mult
        drones += float(frame.drone_eighths or 0) * dr_mult
        drone_brood += float(frame.drone_brood_eighths or 0) * dr_b_mult
        pollen += float(frame.pollen_eighths or 0) * p_mult

    return {
        "brood": brood,
        "food": food,
        "bees": bees,
        "drones": drones,
        "drone_brood": drone_brood,
        "pollen": pollen,
    }

def estimate_varroa(raw_count: int, target_date: date, db: Session) -> tuple[str, float]:
    season = detect_season(target_date)
    multiplier = db.query(VarroaMultiplier).filter(VarroaMultiplier.season == season).first()
    if multiplier is None:
        return season, float(raw_count)
    return season, float(raw_count) * float(multiplier.multiplier)
