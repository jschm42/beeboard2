import os
import sqlite3
import sys
from datetime import datetime
from sqlalchemy.orm import Session

# Add backend root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.apiary import Apiary, ApiaryMembership
from app.models.location import Location
from app.models.administration import FrameType, VarroaMultiplier
from app.models.hive import Hive, HiveBox
from app.models.logbook import (
    LogSession, LogEntry, InspectionDetail, InspectionFrame,
    VarroaCountDetail, VarroaTreatmentDetail, LogEntryImage
)
from app.scripts.seed import seed_database

def parse_date(date_str: str) -> datetime:
    """Parses date from SQLite formats (YYYY-MM-DD or full timestamp)."""
    if not date_str:
        return datetime.utcnow()
    try:
        if " " in date_str:
            date_str = date_str.split(" ")[0]
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return datetime.utcnow().date()

def parse_datetime(dt_str: str) -> datetime:
    """Parses datetime strings from SQLite."""
    if not dt_str:
        return datetime.utcnow()
    # Strip timezone offset if present (e.g. +00:00)
    if "+" in dt_str:
        dt_str = dt_str.split("+")[0]
    try:
        # Django format typically YYYY-MM-DD HH:MM:SS.mmmmmm
        if "." in dt_str:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d")
        except Exception:
            return datetime.utcnow()

def migrate_data(source_db_path: str, target_db: Session):
    if not os.path.exists(source_db_path):
        print(f"Fehler: Quelldatenbank unter '{source_db_path}' nicht gefunden.")
        print("Starte stattdessen das Standard-Datenbank-Seeding...")
        seed_database(target_db)
        return

    print(f"Starte Datenmigration von '{source_db_path}'...")
    src_conn = sqlite3.connect(source_db_path)
    src_conn.row_factory = sqlite3.Row
    src_cursor = src_conn.cursor()

    # Clear target database tables (optional, let's just make sure we drop/create them first)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Zieltabellen zurückgesetzt.")

    # Helper function to check if table exists in source
    def table_exists(name):
        src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return src_cursor.fetchone() is not None

    # 1. Migrate Users
    users_mapped = {}
    if table_exists("accounts_user"):
        print("Migriere Benutzer (accounts_user)...")
        src_cursor.execute("SELECT * FROM accounts_user")
        for row in src_cursor.fetchall():
            # Standard Django user fields mapping
            user = User(
                id=str(row["id"]) if "id" in row.keys() else str(row["password"][:10]), # fallback
                username=row["username"],
                email=row["email"],
                hashed_password=row["password"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                role=row["role"] if "role" in row.keys() else "USER",
                is_active=bool(row["is_active"]),
                is_staff=bool(row["is_staff"]),
                is_superuser=bool(row["is_superuser"]),
                created_at=parse_datetime(row["date_joined"]) if "date_joined" in row.keys() else datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            target_db.add(user)
            users_mapped[row["id"]] = user.id
        target_db.commit()
    else:
        print("Tabelle 'accounts_user' existiert nicht. Erstelle Standard-Admin...")
        admin = User(
            username="admin",
            email="admin@beeboard.de",
            hashed_password="pbkdf2_sha256$870000$somepbkdfhashplaceholder$", # placeholder
            role="SYSTEM_ADMIN",
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        target_db.add(admin)
        target_db.commit()
        users_mapped[1] = admin.id

    # 2. Migrate FrameTypes & VarroaMultipliers
    if table_exists("administration_frametype"):
        print("Migriere Rahmenmaße (administration_frametype)...")
        src_cursor.execute("SELECT * FROM administration_frametype")
        for row in src_cursor.fetchall():
            ft = FrameType(
                id=str(row["id"]),
                name=row["name"],
                is_default=bool(row["is_default"]),
                brood_multiplier=float(row["brood_multiplier"]),
                food_multiplier=float(row["food_multiplier"]),
                bee_multiplier=float(row["bee_multiplier"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(ft)
        target_db.commit()
    else:
        # Fallback seeding
        print("FrameType Tabelle fehlt in Quelle. Seede Standard-Rahmenmaße...")
        seed_database(target_db)

    # 3. Migrate VarroaMultipliers
    if table_exists("administration_varroamultiplier"):
        print("Migriere VarroaMultiplikatoren (administration_varroamultiplier)...")
        src_cursor.execute("SELECT * FROM administration_varroamultiplier")
        for row in src_cursor.fetchall():
            vm = VarroaMultiplier(
                id=str(row["id"]),
                season=row["season"],
                multiplier=float(row["multiplier"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(vm)
        target_db.commit()

    # 4. Migrate Apiaries
    if table_exists("apiaries_apiary"):
        print("Migriere Imkereien (apiaries_apiary)...")
        src_cursor.execute("SELECT * FROM apiaries_apiary")
        for row in src_cursor.fetchall():
            apiary = Apiary(
                id=str(row["id"]),
                name=row["name"],
                notes=row["notes"],
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(apiary)
        target_db.commit()

    # 5. Migrate ApiaryMemberships
    if table_exists("apiaries_apiarymembership"):
        print("Migriere Imkerei-Mitgliedschaften (apiaries_apiarymembership)...")
        src_cursor.execute("SELECT * FROM apiaries_apiarymembership")
        for row in src_cursor.fetchall():
            # Check if user still exists
            uid = row["user_id"]
            if uid in users_mapped:
                mem = ApiaryMembership(
                    id=str(row["id"]),
                    apiary_id=str(row["apiary_id"]),
                    user_id=users_mapped[uid],
                    role=row["role"] if "role" in row.keys() else "USER",
                    created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                    updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
                )
                target_db.add(mem)
        target_db.commit()

    # 6. Migrate Locations
    if table_exists("locations_location"):
        print("Migriere Standorte (locations_location)...")
        src_cursor.execute("SELECT * FROM locations_location")
        for row in src_cursor.fetchall():
            loc = Location(
                id=str(row["id"]),
                name=row["name"],
                address=row["address"],
                latitude=float(row["latitude"]) if row["latitude"] is not None else None,
                longitude=float(row["longitude"]) if row["longitude"] is not None else None,
                notes=row["notes"],
                apiary_id=str(row["apiary_id"]),
                created_by_id=users_mapped.get(row["created_by_id"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(loc)
        target_db.commit()

    # 7. Migrate Hives
    if table_exists("hives_hive"):
        print("Migriere Bienenvölker (hives_hive)...")
        src_cursor.execute("SELECT * FROM hives_hive")
        for row in src_cursor.fetchall():
            hive = Hive(
                id=str(row["id"]),
                name=row["name"],
                location_id=str(row["location_id"]),
                frame_type_id=str(row["frame_type_id"]),
                queen_year=row["queen_year"],
                is_active=bool(row["is_active"]),
                notes=row["notes"],
                image_path=row["image"] if "image" in row.keys() else None,
                apiary_id=str(row["apiary_id"]),
                created_by_id=users_mapped.get(row["created_by_id"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(hive)
        target_db.commit()

    # 8. Migrate HiveBoxes
    if table_exists("hives_hivebox"):
        print("Migriere Zargen (hives_hivebox)...")
        src_cursor.execute("SELECT * FROM hives_hivebox")
        for row in src_cursor.fetchall():
            box = HiveBox(
                id=str(row["id"]),
                hive_id=str(row["hive_id"]),
                order=row["order"],
                frame_type_id=str(row["frame_type_id"]),
                frame_count=row["frame_count"],
                box_type=row["box_type"],
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(box)
        target_db.commit()

    # 9. Migrate LogSessions
    if table_exists("logbook_logsession"):
        print("Migriere Logbuch-Sessions (logbook_logsession)...")
        src_cursor.execute("SELECT * FROM logbook_logsession")
        for row in src_cursor.fetchall():
            sess = LogSession(
                id=str(row["id"]),
                title=row["title"],
                hive_id=str(row["hive_id"]) if row["hive_id"] is not None else None,
                apiary_id=str(row["apiary_id"]),
                created_by_id=users_mapped.get(row["created_by_id"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(sess)
        target_db.commit()

    # 10. Migrate LogEntries
    if table_exists("logbook_logentry"):
        print("Migriere Logbucheinträge (logbook_logentry)...")
        src_cursor.execute("SELECT * FROM logbook_logentry")
        for row in src_cursor.fetchall():
            entry = LogEntry(
                id=str(row["id"]),
                hive_id=str(row["hive_id"]),
                session_id=str(row["session_id"]) if row["session_id"] is not None else None,
                date=parse_date(row["date"]),
                entry_type=row["entry_type"],
                notes=row["notes"],
                apiary_id=str(row["apiary_id"]),
                created_by_id=users_mapped.get(row["created_by_id"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(entry)
        target_db.commit()

    # 11. Migrate InspectionDetails & InspectionFrames
    if table_exists("logbook_inspectiondetail"):
        print("Migriere Inspektionsdetails (logbook_inspectiondetail)...")
        src_cursor.execute("SELECT * FROM logbook_inspectiondetail")
        for row in src_cursor.fetchall():
            det = InspectionDetail(
                id=str(row["id"]),
                log_entry_id=str(row["log_entry_id"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(det)
        target_db.commit()

    if table_exists("logbook_inspectionframe"):
        print("Migriere Inspektionswaben (logbook_inspectionframe)...")
        src_cursor.execute("SELECT * FROM logbook_inspectionframe")
        for row in src_cursor.fetchall():
            frame = InspectionFrame(
                id=str(row["id"]),
                inspection_id=str(row["inspection_id"]),
                frame_number=row["frame_number"],
                side=row["side"],
                brood_eighths=row["brood_eighths"],
                food_eighths=row["food_eighths"],
                bee_eighths=row["bee_eighths"],
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(frame)
        target_db.commit()

    # 12. Migrate VarroaCountDetails
    if table_exists("logbook_varroacountdetail"):
        print("Migriere Varroa-Zählung (logbook_varroacountdetail)...")
        src_cursor.execute("SELECT * FROM logbook_varroacountdetail")
        for row in src_cursor.fetchall():
            vcd = VarroaCountDetail(
                id=str(row["id"]),
                log_entry_id=str(row["log_entry_id"]),
                raw_count=row["raw_count"],
                season=row["season"],
                estimated_total=float(row["estimated_total"]),
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(vcd)
        target_db.commit()

    # 13. Migrate VarroaTreatmentDetails
    if table_exists("logbook_varroatreatmentdetail"):
        print("Migriere Varroa-Behandlungen (logbook_varroatreatmentdetail)...")
        src_cursor.execute("SELECT * FROM logbook_varroatreatmentdetail")
        for row in src_cursor.fetchall():
            vtd = VarroaTreatmentDetail(
                id=str(row["id"]),
                log_entry_id=str(row["log_entry_id"]),
                product=row["product"],
                dosage=row["dosage"],
                treatment_notes=row["treatment_notes"] if "treatment_notes" in row.keys() else "",
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(vtd)
        target_db.commit()

    # 14. Migrate LogEntryImages
    if table_exists("logbook_logentryimage"):
        print("Migriere Logbucheintrag-Bilder (logbook_logentryimage)...")
        src_cursor.execute("SELECT * FROM logbook_logentryimage")
        for row in src_cursor.fetchall():
            img = LogEntryImage(
                id=str(row["id"]),
                log_entry_id=str(row["log_entry_id"]),
                image_path=row["image"],
                thumbnail_path=row["thumbnail"] if "thumbnail" in row.keys() else None,
                created_at=parse_datetime(row["created_at"]) if "created_at" in row.keys() else datetime.utcnow(),
                updated_at=parse_datetime(row["updated_at"]) if "updated_at" in row.keys() else datetime.utcnow()
            )
            target_db.add(img)
        target_db.commit()

    src_conn.close()
    print("Datenmigration erfolgreich abgeschlossen!")

if __name__ == "__main__":
    db = SessionLocal()
    # Attempt to locate source database in the original workspace
    source_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "beeboard", "data", "db.sqlite3"))
    try:
        migrate_data(source_path, db)
    finally:
        db.close()
