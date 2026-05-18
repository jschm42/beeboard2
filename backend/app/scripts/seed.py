from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.administration import FrameType, VarroaMultiplier

def seed_database(db: Session):
    print("Starte Datenbank-Seeding...")
    
    # 1. Seed Frame Types
    frame_types = [
        {
            "name": "Zander",
            "is_default": True,
            "brood_multiplier": 1.00,
            "food_multiplier": 1.00,
            "bee_multiplier": 1.00,
        },
        {
            "name": "Dadant",
            "is_default": False,
            "brood_multiplier": 1.45,
            "food_multiplier": 1.45,
            "bee_multiplier": 1.45,
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

    db.commit()
    print("Datenbank-Seeding erfolgreich abgeschlossen!")

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
