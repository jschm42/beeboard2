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

def calculate_inspection_totals(boxes, db: Session = None):
    """
    Calculates total brood, food, bees, drones, drone brood, and pollen from list of InspectionBox models.
    Each box can have direct totals OR eighth-based inputs.
    """
    brood = 0.0
    food = 0.0
    bees = 0.0
    drones = 0.0
    drone_brood = 0.0
    pollen = 0.0

    for box in boxes:
        # Retrieve the hive and the specific HiveBox frame type
        inspection = getattr(box, "inspection", None)
        if inspection:
            log_entry = getattr(inspection, "log_entry", None)
            hive = getattr(log_entry, "hive", None) if log_entry else None
        else:
            hive = None

        frame_type = None
        if hive:
            # Match box_index to determine the correct HiveBox (sorted by order)
            if hasattr(hive, "boxes"):
                sorted_hive_boxes = sorted(hive.boxes, key=lambda b: b.order)
                box_idx = getattr(box, "box_index", 0)
                if 0 <= box_idx < len(sorted_hive_boxes):
                    frame_type = sorted_hive_boxes[box_idx].frame_type
                else:
                    frame_type = hive.frame_type
            else:
                frame_type = getattr(hive, "frame_type", None)
        
        b_mult = float(frame_type.brood_multiplier) if frame_type else 1.0
        f_mult = float(frame_type.food_multiplier) if frame_type else 1.0
        bee_mult = float(frame_type.bee_multiplier) if frame_type else 1.0
        dr_mult = float(frame_type.drone_multiplier or 1.0) if frame_type else 1.0
        dr_b_mult = float(frame_type.drone_brood_multiplier or 1.0) if frame_type else 1.0
        p_mult = float(frame_type.pollen_multiplier or 1.0) if frame_type else 1.0

        if box.brood_eighths is not None:
            brood += float(box.brood_eighths) * b_mult
        else:
            brood += float(box.brood_total or 0)

        if box.food_eighths is not None:
            food += float(box.food_eighths) * f_mult
        else:
            food += float(box.food_total or 0)

        if box.bee_eighths is not None:
            bees += float(box.bee_eighths) * bee_mult
        else:
            bees += float(box.bee_total or 0)

        if box.drone_eighths is not None:
            drones += float(box.drone_eighths) * dr_mult
        else:
            drones += float(box.drone_total or 0)

        if box.drone_brood_eighths is not None:
            drone_brood += float(box.drone_brood_eighths) * dr_b_mult
        else:
            drone_brood += float(box.drone_brood_total or 0)

        if box.pollen_eighths is not None:
            pollen += float(box.pollen_eighths) * p_mult
        else:
            pollen += float(box.pollen_total or 0)

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
