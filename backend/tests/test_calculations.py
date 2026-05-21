from datetime import date
from sqlalchemy.orm import Session

from app.services.calculations import detect_season, calculate_inspection_totals, estimate_varroa
from app.models.administration import FrameType

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
        def __init__(self, brood, food, bee, drone=1.0, drone_brood=1.0, pollen=1.0):
            self.brood_multiplier = brood
            self.food_multiplier = food
            self.bee_multiplier = bee
            self.drone_multiplier = drone
            self.drone_brood_multiplier = drone_brood
            self.pollen_multiplier = pollen

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
        def __init__(self, inspection, b, f, be, dr=0, dr_b=0, po=0):
            self.inspection = inspection
            self.brood_eighths = b
            self.food_eighths = f
            self.bee_eighths = be
            self.drone_eighths = dr
            self.drone_brood_eighths = dr_b
            self.pollen_eighths = po

    hive_zander = MockHive(zander)
    le_z = MockLogEntry(hive_zander)
    insp_z = MockInspection(le_z)

    # 2 Waben-Seiten, Zander Multipliers: brood=400, food=125, bees=125, drones=100, drone_brood=230, pollen=40
    frames_z = [
        MockInspectionFrame(insp_z, 4, 2, 6, 1, 2, 3),
        MockInspectionFrame(insp_z, 2, 4, 2, 3, 1, 0),
    ]

    totals_z = calculate_inspection_totals(frames_z, db)
    # (4+2)*400 = 2400 brood
    # (2+4)*125 = 750 food
    # (6+2)*125 = 1000 bees
    # (1+3)*100 = 400 drones
    # (2+1)*230 = 690 drone_brood
    # (3+0)*40 = 120 pollen
    assert totals_z["brood"] == 2400.0
    assert totals_z["food"] == 750.0
    assert totals_z["bees"] == 1000.0
    assert totals_z["drones"] == 400.0
    assert totals_z["drone_brood"] == 690.0
    assert totals_z["pollen"] == 120.0

    # Dadant Multipliers: brood=564, food=176, bees=176, drones=141, drone_brood=324, pollen=56
    hive_dadant = MockHive(dadant)
    le_d = MockLogEntry(hive_dadant)
    insp_d = MockInspection(le_d)
    frames_d = [
        MockInspectionFrame(insp_d, 4, 2, 6, 2, 1, 5),
    ]

    totals_d = calculate_inspection_totals(frames_d, db)
    # 4 * 564 = 2256 brood
    # 2 * 176 = 352 food
    # 6 * 176 = 1056 bees
    # 2 * 141 = 282 drones
    # 1 * 324 = 324 drone_brood
    # 5 * 56 = 280 pollen
    assert totals_d["brood"] == 2256.0
    assert totals_d["food"] == 352.0
    assert totals_d["bees"] == 1056.0
    assert totals_d["drones"] == 282.0
    assert totals_d["drone_brood"] == 324.0
    assert totals_d["pollen"] == 280.0

def test_estimate_varroa(db: Session):
    # SUMMER Varroa multiplier is seeded as 300.00
    season, estimate = estimate_varroa(5, date(2026, 7, 10), db)
    assert season == "SUMMER"
    assert estimate == 5 * 300.00

    # WINTER Varroa multiplier is seeded as 180.00
    season, estimate = estimate_varroa(2, date(2026, 12, 1), db)
    assert season == "WINTER"
    assert estimate == 2 * 180.00
