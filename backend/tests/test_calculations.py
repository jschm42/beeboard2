from datetime import date
from sqlalchemy.orm import Session

from app.services.calculations import detect_season, calculate_inspection_totals, estimate_varroa
from app.models.administration import FrameType
from app.models.logbook import InspectionFrame

def test_detect_season():
    assert detect_season(date(2026, 4, 15)) == "SPRING"
    assert detect_season(date(2026, 7, 20)) == "SUMMER"
    assert detect_season(date(2026, 10, 5)) == "AUTUMN"
    assert detect_season(date(2026, 1, 12)) == "WINTER"

def test_calculate_inspection_totals(db: Session):
    # Retrieve Zander and Dadant frame types seeded by default
    zander = db.query(FrameType).filter(FrameType.name == "Zander").first()
    dadant = db.query(FrameType).filter(FrameType.name == "Dadant").first()

    assert zander is not None
    assert dadant is not None

    # Mock dynamic frame types that mimic the nested ORM relationships
    class MockFrameType:
        def __init__(self, brood, food, bee):
            self.brood_multiplier = brood
            self.food_multiplier = food
            self.bee_multiplier = bee

    class MockHive:
        def __init__(self, ft):
            self.frame_type = ft

    class MockLogEntry:
        def __init__(self, hive):
            self.hive = hive

    class MockInspection:
        def __init__(self, le):
            self.log_entry = le

    class MockInspectionFrame:
        def __init__(self, inspection, b, f, be):
            self.inspection = inspection
            self.brood_eighths = b
            self.food_eighths = f
            self.bee_eighths = be

    hive_zander = MockHive(zander)
    le_z = MockLogEntry(hive_zander)
    insp_z = MockInspection(le_z)

    # 2 Waben-Seiten, Zander Multiplikator = 1.0
    frames_z = [
        MockInspectionFrame(insp_z, 4, 2, 6),
        MockInspectionFrame(insp_z, 2, 4, 2),
    ]

    totals_z = calculate_inspection_totals(frames_z, db)
    # 4*1 + 2*1 = 6 brood
    # 2*1 + 4*1 = 6 food
    # 6*1 + 2*1 = 8 bees
    assert totals_z["brood"] == 6.0
    assert totals_z["food"] == 6.0
    assert totals_z["bees"] == 8.0

    # Dadant Multiplikator = 1.45
    hive_dadant = MockHive(dadant)
    le_d = MockLogEntry(hive_dadant)
    insp_d = MockInspection(le_d)
    frames_d = [
        MockInspectionFrame(insp_d, 4, 2, 6),
    ]

    totals_d = calculate_inspection_totals(frames_d, db)
    # 4 * 1.45 = 5.8 brood
    # 2 * 1.45 = 2.9 food
    # 6 * 1.45 = 8.7 bees
    assert abs(totals_d["brood"] - 5.8) < 0.001
    assert abs(totals_d["food"] - 2.9) < 0.001
    assert abs(totals_d["bees"] - 8.7) < 0.001

def test_estimate_varroa(db: Session):
    # SUMMER Varroa multiplier is seeded as 300.00
    season, estimate = estimate_varroa(5, date(2026, 7, 10), db)
    assert season == "SUMMER"
    assert estimate == 5 * 300.00

    # WINTER Varroa multiplier is seeded as 180.00
    season, estimate = estimate_varroa(2, date(2026, 12, 1), db)
    assert season == "WINTER"
    assert estimate == 2 * 180.00
