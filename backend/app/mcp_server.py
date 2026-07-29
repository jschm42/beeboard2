import os
import hashlib
from datetime import date, datetime
from typing import Optional
from fastmcp import FastMCP
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User
from app.models.apiary import Apiary, ApiaryMembership
from app.models.hive import Hive
from app.models.logbook import LogEntry
from app.models.api_key import ApiKey

mcp = FastMCP("BeeBoard")

def get_user_from_env(db: Session) -> Optional[User]:
    """Resolves the user based on BEEBOARD_API_KEY environment variable.
    
    Falls back to the first active user in the database for ease of local use.
    """
    api_key = os.environ.get("BEEBOARD_API_KEY")
    if api_key:
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        key_record = db.query(ApiKey).filter(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True
        ).first()
        if key_record:
            user = db.query(User).filter(User.id == key_record.user_id).first()
            if user and user.is_active:
                return user
                
    # Fallback to the first active user
    user = db.query(User).filter(User.is_active == True).first()
    return user

@mcp.tool()
def list_apiaries() -> str:
    """Lists all apiaries (Bienenstände) the user has access to.
    
    Returns a list of apiaries with their names and IDs.
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer in der Datenbank gefunden."
        
        if user.role == "SYSTEM_ADMIN":
            apiaries = db.query(Apiary).all()
        else:
            apiaries = db.query(Apiary).join(ApiaryMembership).filter(
                ApiaryMembership.user_id == user.id
            ).all()
            
        if not apiaries:
            return "Keine Bienenstände gefunden."
            
        result = []
        for a in apiaries:
            result.append(f"- {a.name} (ID: {a.id})")
        return "\n".join(result)
    finally:
        db.close()

@mcp.tool()
def list_hives(apiary_id: str) -> str:
    """Lists all hives (Bienenvölker) in a given apiary (Bienenstand).
    
    Args:
        apiary_id: The ID of the apiary.
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        from app.routers.apiaries import check_access
        try:
            check_access(apiary_id, user, db)
        except Exception as e:
            return f"Zugriff verweigert oder Fehler: {str(e)}"
            
        hives = db.query(Hive).filter(Hive.apiary_id == apiary_id).order_by(Hive.name).all()
        if not hives:
            return "Keine Völker an diesem Stand gefunden."
            
        result = []
        for h in hives:
            active_str = "Aktiv" if h.is_active else "Inaktiv"
            result.append(f"- {h.name} (ID: {h.id}) - {active_str}")
        return "\n".join(result)
    finally:
        db.close()

@mcp.tool()
def search_hive_by_name(name: str) -> str:
    """Searches for a hive (Bienenvolk) by name (case-insensitive) in the user's authorized apiaries.
    
    Returns the hive details including its hive_id and apiary_id.
    
    Args:
        name: The name of the hive (e.g. 'Volk 1').
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        if user.role == "SYSTEM_ADMIN":
            apiary_ids = [a.id for a in db.query(Apiary).all()]
        else:
            apiary_ids = [
                m.apiary_id for m in db.query(ApiaryMembership).filter(
                    ApiaryMembership.user_id == user.id
                ).all()
            ]
            
        hives = db.query(Hive).filter(
            Hive.name.ilike(name),
            Hive.apiary_id.in_(apiary_ids)
        ).all()
        
        if not hives:
            return f"Kein Volk mit dem Namen '{name}' in Ihren Bienenständen gefunden."
            
        result = []
        for h in hives:
            apiary_name = h.apiary.name if h.apiary else "Unbekannt"
            result.append(
                f"Volk: {h.name}\n"
                f"- ID (hive_id): {h.id}\n"
                f"- Bienenstand: {apiary_name} (ID: {h.apiary_id})\n"
                f"- Status: {'Aktiv' if h.is_active else 'Inaktiv'}\n"
                f"- Königinnenjahr: {h.queen_year or 'Unbekannt'}"
            )
        return "\n\n".join(result)
    finally:
        db.close()

@mcp.tool()
def create_journal_note(hive_id: str, notes: str, date_str: str = None) -> str:
    """Creates a general logbook note for a specific hive.
    
    Args:
        hive_id: The ID of the hive (use search_hive_by_name to find this first!).
        notes: The text content of the note (e.g. 'Königin gefunden', 'Futterwabe zugegeben').
        date_str: Optional date in YYYY-MM-DD format (defaults to today's date).
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        hive = db.query(Hive).filter(Hive.id == hive_id).first()
        if not hive:
            return f"Fehler: Volk mit ID {hive_id} existiert nicht."
            
        from app.routers.apiaries import check_access
        try:
            check_access(hive.apiary_id, user, db)
        except Exception as e:
            return f"Zugriff verweigert: {str(e)}"
            
        entry_date = date.today()
        if date_str:
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return f"Fehler: Ungültiges Datumsformat '{date_str}'. Bitte verwenden Sie YYYY-MM-DD."
                
        entry = LogEntry(
            hive_id=hive_id,
            apiary_id=hive.apiary_id,
            created_by_id=user.id,
            date=entry_date,
            entry_type="GENERAL",
            notes=notes
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        return (
            f"Notiz erfolgreich erstellt!\n"
            f"- Volk: {hive.name}\n"
            f"- Datum: {entry.date}\n"
            f"- Eintrag-ID: {entry.id}\n"
            f"- Inhalt: {entry.notes}"
        )
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
