import os
import hashlib
from datetime import date, datetime
from typing import Optional
from fastmcp import FastMCP
from sqlalchemy.orm import Session
from fastapi import HTTPException

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
            notes=notes,
            created_via_mcp=True
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

@mcp.tool()
def list_sales_products(is_active: bool = True) -> str:
    """Lists all honey product configurations for the user.
    
    Args:
        is_active: If True, lists only active products. Otherwise lists all.
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        from app.models.sales import ProductConfig
        query = db.query(ProductConfig).filter(ProductConfig.created_by_id == user.id)
        if is_active:
            query = query.filter(ProductConfig.is_active == True)
        products = query.order_by(ProductConfig.name).all()
        
        if not products:
            return "Keine Produktkonfigurationen gefunden."
            
        result = []
        for p in products:
            status_str = "Aktiv" if p.is_active else "Inaktiv"
            stock_str = f"{p.stock} (Min: {p.min_stock})" if p.manage_stock else "Nicht verwaltet"
            batch_req = "Ja" if p.requires_batch_selection else "Nein"
            result.append(
                f"- ID: {p.id}\n"
                f"  Name: {p.name}\n"
                f"  Preis: {p.price} EUR (Steuersatz: {p.tax_rate}%)\n"
                f"  Honigtyp: {p.honey_type or 'Unbekannt'}\n"
                f"  Bestand: {stock_str}\n"
                f"  Charge erforderlich: {batch_req}\n"
                f"  Status: {status_str}"
            )
        return "\n\n".join(result)
    finally:
        db.close()

@mcp.tool()
def create_honey_sale(
    product_id: str,
    quantity: float,
    sales_channel: str = "direktverkauf",
    total_price: float = None,
    buyer: str = None,
    notes: str = None,
    batch_id: str = None,
    sale_date_str: str = None
) -> str:
    """Records a new honey sale. Automatically updates product stock if configured.
    
    Args:
        product_id: The ID of the product config.
        quantity: Quantity sold.
        sales_channel: The sales channel (e.g. direktverkauf, online, email, verkaufsstand).
        total_price: Optional total price (defaults to quantity * product price).
        buyer: Optional buyer name.
        notes: Optional notes.
        batch_id: Optional honey batch ID (required if product requires batch selection).
        sale_date_str: Optional date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format (defaults to current time).
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        from app.models.sales import ProductConfig, HoneySale
        from app.models.honey_batch import HoneyBatch
        from app.routers.apiaries import check_access
        
        product = db.query(ProductConfig).filter(
            ProductConfig.id == product_id,
            ProductConfig.created_by_id == user.id
        ).first()
        if not product:
            return f"Fehler: Produktkonfiguration mit ID {product_id} nicht gefunden."
            
        if batch_id:
            batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
            if not batch:
                return f"Fehler: Honig-Charge mit ID {batch_id} nicht gefunden."
            try:
                check_access(batch.apiary_id, user, db)
            except HTTPException as e:
                return f"Zugriff verweigert auf Charge {batch_id}: {e.detail}"
                
        if product.requires_batch_selection and not batch_id:
            return f"Fehler: Für das Produkt '{product.name}' ist die Angabe einer Losnummer (Charge) zwingend erforderlich."
            
        # Parse date if provided
        sale_date = datetime.now()
        if sale_date_str:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    sale_date = datetime.strptime(sale_date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return f"Fehler: Ungültiges Datumsformat '{sale_date_str}'. Verwenden Sie YYYY-MM-DD oder YYYY-MM-DD HH:MM."
                
        # Compute price
        if total_price is None:
            total_price = product.price * quantity
            
        # Deduct stock if manage_stock is True
        if product.manage_stock:
            product.stock -= quantity
            
        sale = HoneySale(
            sale_date=sale_date,
            product_id=product_id,
            batch_id=batch_id,
            quantity=quantity,
            total_price=total_price,
            sales_channel=sales_channel,
            notes=notes,
            buyer=buyer,
            created_by_id=user.id
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)
        
        batch_info = f" (Charge-ID: {batch_id})" if batch_id else ""
        return (
            f"Verkauf erfolgreich erfasst!\n"
            f"- Verkauf-ID: {sale.id}\n"
            f"- Produkt: {product.name}\n"
            f"- Menge: {quantity}\n"
            f"- Gesamtpreis: {total_price} EUR\n"
            f"- Verkaufskanal: {sales_channel}\n"
            f"- Käufer: {buyer or 'Keine Angabe'}\n"
            f"- Datum: {sale.sale_date.strftime('%Y-%m-%d %H:%M')}{batch_info}"
        )
    finally:
        db.close()

@mcp.tool()
def list_honey_sales(start_date_str: str = None, end_date_str: str = None) -> str:
    """Lists honey sales for the user, optionally filtered by a date range.
    
    Args:
        start_date_str: Optional start date (YYYY-MM-DD).
        end_date_str: Optional end date (YYYY-MM-DD).
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        from app.models.sales import HoneySale
        query = db.query(HoneySale).filter(HoneySale.created_by_id == user.id)
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                query = query.filter(HoneySale.sale_date >= start_date)
            except ValueError:
                return f"Fehler: Ungültiges start_date Format '{start_date_str}'. Bitte verwenden Sie YYYY-MM-DD."
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                query = query.filter(HoneySale.sale_date <= end_date)
            except ValueError:
                return f"Fehler: Ungültiges end_date Format '{end_date_str}'. Bitte verwenden Sie YYYY-MM-DD."
                
        sales = query.order_by(HoneySale.sale_date.desc()).all()
        if not sales:
            return "Keine Verkäufe im angegebenen Zeitraum gefunden."
            
        result = []
        for s in sales:
            prod_name = s.product.name if s.product else "Gelöschtes Produkt"
            date_str = s.sale_date.strftime("%Y-%m-%d %H:%M")
            result.append(
                f"- Datum: {date_str}\n"
                f"  Produkt: {prod_name} (ID: {s.product_id})\n"
                f"  Menge: {s.quantity}\n"
                f"  Gesamtpreis: {s.total_price} EUR\n"
                f"  Kanal: {s.sales_channel}\n"
                f"  Käufer: {s.buyer or 'Unbekannt'}\n"
                f"  Notiz: {s.notes or '-'}"
            )
        return "\n\n".join(result)
    finally:
        db.close()

@mcp.tool()
def get_hive_inspection_stats(hive_id: str, year: int = None, season: str = None) -> str:
    """Retrieves aggregated inspection statistics (brood, food, bees, etc.) for a specific hive over time.
    
    Args:
        hive_id: The ID of the hive.
        year: Optional calendar year filter.
        season: Optional season filter ('SPRING', 'SUMMER', 'AUTUMN', 'WINTER').
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        hive = db.query(Hive).filter(Hive.id == hive_id).first()
        if not hive:
            return f"Fehler: Volk mit ID {hive_id} nicht gefunden."
            
        from app.routers.apiaries import check_access
        try:
            check_access(hive.apiary_id, user, db)
        except HTTPException as e:
            return f"Zugriff verweigert: {e.detail}"
            
        from sqlalchemy import extract
        from sqlalchemy.orm import joinedload
        from app.models.logbook import LogEntry, InspectionDetail
        from app.services.calculations import calculate_inspection_totals, detect_season
        
        query = db.query(LogEntry).filter(
            LogEntry.hive_id == hive_id,
            LogEntry.entry_type == "INSPECTION"
        )
        
        if year:
            query = query.filter(extract('year', LogEntry.date) == year)
            
        query = query.options(
            joinedload(LogEntry.inspection_detail).joinedload(InspectionDetail.boxes)
        ).order_by(LogEntry.date.asc())
        
        entries = query.all()
        if not entries:
            return f"Keine Inspektionseinträge für das Volk '{hive.name}' gefunden."
            
        result = [f"Inspektionsstatistiken für Volk '{hive.name}' (ID: {hive_id}):"]
        
        has_matched_data = False
        for entry in entries:
            if not entry.inspection_detail or not entry.inspection_detail.boxes:
                continue
                
            ent_season = detect_season(entry.date)
            if season and ent_season != season:
                continue
                
            has_matched_data = True
            totals = calculate_inspection_totals(entry.inspection_detail.boxes, db)
            
            notes_str = f" | Notizen: {entry.notes}" if entry.notes else ""
            result.append(
                f"- Datum: {entry.date.isoformat()} ({ent_season})\n"
                f"  Brutwaben: {totals.get('brood', 0.0):.1f} | Futterwaben: {totals.get('food', 0.0):.1f} | Bienen-Gassen: {totals.get('bees', 0.0):.1f}\n"
                f"  Drohnen: {totals.get('drones', 0.0):.1f} | Drohnenbrut: {totals.get('drone_brood', 0.0):.1f} | Pollen: {totals.get('pollen', 0.0):.1f}{notes_str}"
            )
            
        if not has_matched_data:
            return "Keine passenden Inspektionsdaten mit den angegebenen Filtern gefunden."
            
        return "\n\n".join(result)
    finally:
        db.close()

@mcp.tool()
def list_tasks(
    apiary_id: str,
    is_completed: bool = None,
    hive_id: str = None,
    priority: str = None
) -> str:
    """Lists calendar tasks in an authorized apiary with optional filters.
    
    Args:
        apiary_id: The ID of the apiary.
        is_completed: Optional filter for completion status (True/False).
        hive_id: Optional filter for a specific hive ID.
        priority: Optional filter for priority ('LOW', 'MEDIUM', 'HIGH').
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        from app.routers.apiaries import check_access
        try:
            check_access(apiary_id, user, db)
        except HTTPException as e:
            return f"Zugriff verweigert: {e.detail}"
            
        from app.models.task import Task
        from sqlalchemy.orm import joinedload
        
        query = db.query(Task).options(
            joinedload(Task.hive)
        ).filter(Task.apiary_id == apiary_id)
        
        if is_completed is not None:
            query = query.filter(Task.is_completed == is_completed)
        if hive_id:
            query = query.filter(Task.hive_id == hive_id)
        if priority:
            query = query.filter(Task.priority == priority)
            
        tasks = query.order_by(Task.is_completed.asc(), Task.due_date.asc()).all()
        if not tasks:
            return "Keine Aufgaben gefunden."
            
        result = []
        for t in tasks:
            status_str = "Abgeschlossen" if t.is_completed else "Offen"
            due_str = t.due_date.strftime("%Y-%m-%d") if t.due_date else "Kein Datum"
            hive_str = f" (Volk: {t.hive.name})" if t.hive else ""
            desc_str = f"\n  Beschreibung: {t.description}" if t.description else ""
            result.append(
                f"- ID: {t.id}\n"
                f"  Titel: {t.title}{hive_str}\n"
                f"  Fällig am: {due_str} | Priorität: {t.priority} | Status: {status_str}{desc_str}"
            )
        return "\n\n".join(result)
    finally:
        db.close()

@mcp.tool()
def create_task(
    apiary_id: str,
    title: str,
    description: str = None,
    due_date_str: str = None,
    priority: str = "MEDIUM",
    hive_id: str = None,
    is_recurring: bool = False,
    recurrence_interval_type: str = None,
    recurrence_interval_value: int = 1,
    recurrence_end_date_str: str = None
) -> str:
    """Creates a new calendar task inside an authorized apiary.
    
    Args:
        apiary_id: The ID of the apiary.
        title: Title of the task.
        description: Optional details.
        due_date_str: Optional due date (YYYY-MM-DD).
        priority: Priority ('LOW', 'MEDIUM', 'HIGH').
        hive_id: Optional hive ID to associate with.
        is_recurring: Set to True for recurring tasks.
        recurrence_interval_type: Type of recurrence ('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY').
        recurrence_interval_value: Recurrence frequency (default 1).
        recurrence_end_date_str: Optional end date for recurrence (YYYY-MM-DD).
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        from app.routers.apiaries import check_access
        try:
            check_access(apiary_id, user, db)
        except HTTPException as e:
            return f"Zugriff verweigert: {e.detail}"
            
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                return f"Fehler: Ungültiges Datumsformat für Fälligkeitsdatum '{due_date_str}'. Bitte verwenden Sie YYYY-MM-DD."
                
        rec_end_date = None
        if recurrence_end_date_str:
            try:
                rec_end_date = datetime.strptime(recurrence_end_date_str, "%Y-%m-%d").date()
            except ValueError:
                return f"Fehler: Ungültiges Datumsformat für Enddatum '{recurrence_end_date_str}'. Bitte verwenden Sie YYYY-MM-DD."
                
        if hive_id:
            hive = db.query(Hive).filter(Hive.id == hive_id, Hive.apiary_id == apiary_id).first()
            if not hive:
                return f"Fehler: Volk mit ID {hive_id} existiert nicht in diesem Bienenstand."
                
        from app.models.task import Task
        new_task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            location_id=None,
            hive_id=hive_id,
            is_recurring=is_recurring,
            recurrence_interval_type=recurrence_interval_type,
            recurrence_interval_value=recurrence_interval_value,
            recurrence_end_date=rec_end_date,
            apiary_id=apiary_id,
            created_by_id=user.id
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        hive_info = f" (Volk-ID: {hive_id})" if hive_id else ""
        return (
            f"Aufgabe erfolgreich angelegt!\n"
            f"- Task-ID: {new_task.id}\n"
            f"- Titel: {new_task.title}{hive_info}\n"
            f"- Fällig am: {new_task.due_date or 'Kein Datum'}\n"
            f"- Priorität: {new_task.priority}"
        )
    finally:
        db.close()

@mcp.tool()
def list_treatments(
    apiary_id: str,
    hive_id: str = None,
    start_date_str: str = None,
    end_date_str: str = None
) -> str:
    """Lists treatments recorded in an apiary.
    
    Args:
        apiary_id: The ID of the apiary.
        hive_id: Optional filter for a specific hive.
        start_date_str: Optional start date (YYYY-MM-DD).
        end_date_str: Optional end date (YYYY-MM-DD).
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        from app.routers.apiaries import check_access
        try:
            check_access(apiary_id, user, db)
        except HTTPException as e:
            return f"Zugriff verweigert: {e.detail}"
            
        from app.models.treatment import Treatment
        from sqlalchemy.orm import joinedload
        
        query = db.query(Treatment).join(Hive).filter(Treatment.apiary_id == apiary_id)
        
        if hive_id:
            query = query.filter(Treatment.hive_id == hive_id)
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                query = query.filter(Treatment.date >= start_date)
            except ValueError:
                return f"Fehler: Ungültiges Startdatum '{start_date_str}'. Bitte verwenden Sie YYYY-MM-DD."
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                query = query.filter(Treatment.date <= end_date)
            except ValueError:
                return f"Fehler: Ungültiges Enddatum '{end_date_str}'. Bitte verwenden Sie YYYY-MM-DD."
                
        treatments = query.options(
            joinedload(Treatment.treatment_method),
            joinedload(Treatment.application_type),
            joinedload(Treatment.hive)
        ).order_by(Treatment.date.desc()).all()
        
        if not treatments:
            return "Keine Behandlungen gefunden."
            
        result = []
        for t in treatments:
            method_name = t.treatment_method.name if t.treatment_method else "Unbekannt"
            unit = t.treatment_method.unit if t.treatment_method else "ml"
            app_str = f" | Methode: {t.application_type.name}" if t.application_type else ""
            notes_str = f"\n  Notizen: {t.notes}" if t.notes else ""
            result.append(
                f"- Datum: {t.date.isoformat()}\n"
                f"  Volk: {t.hive.name} (ID: {t.hive_id})\n"
                f"  Mittel: {method_name} | Menge: {t.amount} {unit}{app_str}{notes_str}"
            )
        return "\n\n".join(result)
    finally:
        db.close()

@mcp.tool()
def create_treatment(
    hive_id: str,
    treatment_method_id: str,
    amount: float,
    date_str: str = None,
    application_type_id: str = None,
    notes: str = None
) -> str:
    """Records a new treatment application for a specific hive.
    
    Args:
        hive_id: The ID of the hive.
        treatment_method_id: The ID of the treatment method.
        amount: The dosage amount applied.
        date_str: Optional date in YYYY-MM-DD format (defaults to today).
        application_type_id: Optional ID of the application type.
        notes: Optional comments.
    """
    db = SessionLocal()
    try:
        user = get_user_from_env(db)
        if not user:
            return "Fehler: Kein aktiver Benutzer gefunden."
            
        hive = db.query(Hive).filter(Hive.id == hive_id).first()
        if not hive:
            return f"Fehler: Volk mit ID {hive_id} nicht gefunden."
            
        from app.routers.apiaries import check_access
        try:
            check_access(hive.apiary_id, user, db)
        except HTTPException as e:
            return f"Zugriff verweigert: {e.detail}"
            
        from app.models.treatment import TreatmentMethod, TreatmentApplicationType, Treatment
        
        method = db.query(TreatmentMethod).filter(TreatmentMethod.id == treatment_method_id).first()
        if not method:
            return f"Fehler: Behandlungsmethode mit ID {treatment_method_id} nicht gefunden."
            
        if application_type_id:
            app_type = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.id == application_type_id).first()
            if not app_type:
                return f"Fehler: Applikationsmethode mit ID {application_type_id} nicht gefunden."
                
        treatment_date = date.today()
        if date_str:
            try:
                treatment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return f"Fehler: Ungültiges Datumsformat '{date_str}'. Bitte verwenden Sie YYYY-MM-DD."
                
        treatment = Treatment(
            hive_id=hive_id,
            treatment_method_id=treatment_method_id,
            application_type_id=application_type_id,
            date=treatment_date,
            amount=amount,
            notes=notes,
            apiary_id=hive.apiary_id,
            created_by_id=user.id
        )
        db.add(treatment)
        db.commit()
        db.refresh(treatment)
        
        return (
            f"Behandlung erfolgreich erfasst!\n"
            f"- Behandlung-ID: {treatment.id}\n"
            f"- Volk: {hive.name}\n"
            f"- Methode: {method.name}\n"
            f"- Menge: {amount} {method.unit}\n"
            f"- Datum: {treatment.date}"
        )
    finally:
        db.close()

@mcp.tool()
def list_treatment_methods() -> str:
    """Lists all active treatment methods and their units."""
    db = SessionLocal()
    try:
        from app.models.treatment import TreatmentMethod
        methods = db.query(TreatmentMethod).filter(TreatmentMethod.is_active == True).order_by(TreatmentMethod.name).all()
        if not methods:
            return "Keine Behandlungsmethoden konfiguriert."
        result = []
        for m in methods:
            result.append(f"- ID: {m.id} | Name: {m.name} (Einheit: {m.unit})")
        return "\n".join(result)
    finally:
        db.close()

@mcp.tool()
def list_treatment_application_types() -> str:
    """Lists all active treatment application types."""
    db = SessionLocal()
    try:
        from app.models.treatment import TreatmentApplicationType
        types = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.is_active == True).order_by(TreatmentApplicationType.name).all()
        if not types:
            return "Keine Applikationsmethoden konfiguriert."
        result = []
        for t in types:
            result.append(f"- ID: {t.id} | Name: {t.name}")
        return "\n".join(result)
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
