from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base
from app.models.administration import FrameType, VarroaMultiplier, NumberRange

def seed_database(db: Session):
    print("Starte Datenbank-Seeding...")
    
    # 1. Seed Frame Types
    frame_types = [
        {
            "name": "Zander",
            "is_default": True,
            "brood_multiplier": 400.0,
            "food_multiplier": 125.0,
            "bee_multiplier": 125.0,
            "drone_multiplier": 100.0,
            "drone_brood_multiplier": 230.0,
            "pollen_multiplier": 40.0,
        },
        {
            "name": "DeutschNormal",
            "is_default": False,
            "brood_multiplier": 357.0,
            "food_multiplier": 111.0,
            "bee_multiplier": 111.0,
            "drone_multiplier": 89.0,
            "drone_brood_multiplier": 205.0,
            "pollen_multiplier": 36.0,
        },
        {
            "name": "Langstroth",
            "is_default": False,
            "brood_multiplier": 450.0,
            "food_multiplier": 140.0,
            "bee_multiplier": 140.0,
            "drone_multiplier": 112.0,
            "drone_brood_multiplier": 259.0,
            "pollen_multiplier": 45.0,
        },
        {
            "name": "Dadant",
            "is_default": False,
            "brood_multiplier": 564.0,
            "food_multiplier": 176.0,
            "bee_multiplier": 176.0,
            "drone_multiplier": 141.0,
            "drone_brood_multiplier": 324.0,
            "pollen_multiplier": 56.0,
        },
    ]

    for ft_data in frame_types:
        existing = db.query(FrameType).filter(FrameType.name == ft_data["name"]).first()
        if not existing:
            new_ft = FrameType(**ft_data)
            db.add(new_ft)
            print(f"Erstellt FrameType: {ft_data['name']}")
        else:
            # Update factors if changed
            existing.is_default = ft_data["is_default"]
            existing.brood_multiplier = ft_data["brood_multiplier"]
            existing.food_multiplier = ft_data["food_multiplier"]
            existing.bee_multiplier = ft_data["bee_multiplier"]
            existing.drone_multiplier = ft_data["drone_multiplier"]
            existing.drone_brood_multiplier = ft_data["drone_brood_multiplier"]
            existing.pollen_multiplier = ft_data["pollen_multiplier"]
            print(f"FrameType bereits vorhanden, aktualisiert: {ft_data['name']}")

    # 2. Seed Varroa Multipliers
    multipliers = [
        {"season": "SPRING", "multiplier": 120.00},
        {"season": "SUMMER", "multiplier": 300.00},
        {"season": "AUTUMN", "multiplier": 500.00},
        {"season": "WINTER", "multiplier": 180.00},
    ]

    for mult_data in multipliers:
        existing = db.query(VarroaMultiplier).filter(VarroaMultiplier.season == mult_data["season"]).first()
        if not existing:
            new_mult = VarroaMultiplier(**mult_data)
            db.add(new_mult)
            print(f"Erstellt VarroaMultiplier für Saison: {mult_data['season']} ({mult_data['multiplier']})")
        else:
            existing.multiplier = mult_data["multiplier"]
            print(f"VarroaMultiplier für Saison bereits vorhanden, aktualisiert: {mult_data['season']}")

    # 3. Seed Number Ranges
    ranges = [
        {
            "key": "batch_number",
            "name": "Los-/Chargennummer",
            "prefix": "LOT-",
            "current_value": 1,
            "digits": 4,
            "is_active": True
        },
        {
            "key": "reserve_sample_id",
            "name": "Rückstellproben-ID",
            "prefix": "PRB-",
            "current_value": 1,
            "digits": 4,
            "is_active": True
        }
    ]

    for range_data in ranges:
        existing = db.query(NumberRange).filter(NumberRange.key == range_data["key"]).first()
        if not existing:
            new_range = NumberRange(**range_data)
            db.add(new_range)
            print(f"Erstellt NumberRange: {range_data['name']} (Key: {range_data['key']})")
        else:
            # Do not overwrite current_value, but we can update prefix/digits/name if needed
            existing.name = range_data["name"]
            print(f"NumberRange {range_data['key']} bereits vorhanden.")

    # 4. Seed Treatment Methods & Application Types
    from app.models.treatment import TreatmentMethod, TreatmentApplicationType
    methods = [
        {"name": "Oxalsäure", "unit": "ml", "is_active": True},
        {"name": "Ameisensäure", "unit": "ml", "is_active": True},
        {"name": "Milchsäure", "unit": "ml", "is_active": True},
        {"name": "Thymol", "unit": "g", "is_active": True},
        {"name": "Amitraz-Streifen", "unit": "Streifen", "is_active": True},
    ]

    for method_data in methods:
        existing = db.query(TreatmentMethod).filter(TreatmentMethod.name == method_data["name"]).first()
        if not existing:
            new_method = TreatmentMethod(**method_data)
            db.add(new_method)
            print(f"Erstellt TreatmentMethod: {method_data['name']} ({method_data['unit']})")
        else:
            existing.unit = method_data["unit"]
            existing.is_active = method_data["is_active"]
            print(f"TreatmentMethod {method_data['name']} bereits vorhanden.")

    app_types = [
        {"name": "sprühen", "is_active": True},
        {"name": "verdampfen", "is_active": True},
        {"name": "beträufeln", "is_active": True},
    ]

    for app_data in app_types:
        existing_app = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.name == app_data["name"]).first()
        if not existing_app:
            new_app = TreatmentApplicationType(**app_data)
            db.add(new_app)
            print(f"Erstellt TreatmentApplicationType: {app_data['name']}")
        else:
            existing_app.is_active = app_data["is_active"]
            print(f"TreatmentApplicationType {app_data['name']} bereits vorhanden.")

    db.commit()
    print("Datenbank-Seeding erfolgreich abgeschlossen!")

if __name__ == "__main__":
    # Hinweis: Das Schema wird über Alembic-Migrationen verwaltet (alembic upgrade head).
    # Dieses Script kümmert sich nur um fachliche Stammdaten (FrameTypes, VarroaMultipliers).
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
