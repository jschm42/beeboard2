from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List, Optional
import os
import uuid
from PIL import Image

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.hive import Hive, HiveBox
from app.models.logbook import (
    LogSession, LogEntry, InspectionDetail, InspectionBox,
    VarroaCountDetail, VarroaTreatmentDetail, LogEntryImage
)
from app.schemas.logbook import (
    LogSessionCreate, LogSessionOut, LogEntryCreate, LogEntryOut, LogEntryImageOut
)
from app.routers.apiaries import check_access
from app.services.calculations import estimate_varroa

router = APIRouter(prefix="/logbook", tags=["logbook"])


def get_frame_multipliers(hive: Hive, frame_number: int):
    # Sort boxes by order
    sorted_boxes = sorted(hive.boxes, key=lambda b: b.order)
    current_start = 1
    for box in sorted_boxes:
        current_end = current_start + box.frame_count - 1
        if current_start <= frame_number <= current_end:
            # We found the box! Use this box's frame_type
            ft = box.frame_type
            return (
                float(ft.brood_multiplier),
                float(ft.food_multiplier),
                float(ft.bee_multiplier),
                float(ft.drone_multiplier or 1.0),
                float(ft.drone_brood_multiplier or 1.0),
                float(ft.pollen_multiplier or 1.0)
            )
        current_start = current_end + 1
    
    # Fallback to the hive's main frame_type if frame_number is out of bounds or no boxes configured
    ft = hive.frame_type
    return (
        float(ft.brood_multiplier),
        float(ft.food_multiplier),
        float(ft.bee_multiplier),
        float(ft.drone_multiplier or 1.0),
        float(ft.drone_brood_multiplier or 1.0),
        float(ft.pollen_multiplier or 1.0)
    )

# -----------------
# SESSIONS ENDPOINTS
# -----------------

@router.get("/sessions", response_model=List[LogSessionOut])
def list_sessions(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all working sessions inside an authorized apiary."""
    check_access(apiary_id, current_user, db)
    from app.models.apiary import Apiary
    from app.models.location import Location
    from sqlalchemy import or_
    return db.query(LogSession).options(
        joinedload(LogSession.linked_apiaries),
        joinedload(LogSession.linked_locations),
        joinedload(LogSession.linked_hives)
    ).filter(
        or_(
            LogSession.apiary_id == apiary_id,
            LogSession.linked_apiaries.any(id=apiary_id),
            LogSession.linked_locations.any(apiary_id=apiary_id),
            LogSession.linked_hives.any(apiary_id=apiary_id)
        )
    ).order_by(LogSession.updated_at.desc()).all()

@router.post("/sessions", response_model=LogSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    session_in: LogSessionCreate,
    apiary_id: str = Query(..., description="Scope creation to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new working session scoped to an apiary."""
    check_access(apiary_id, current_user, db)
    
    from app.models.apiary import Apiary
    from app.models.location import Location

    apiaries = []
    locations = []
    hives = []
    
    if session_in.scope_type == "APIARY":
        apiaries = db.query(Apiary).filter(Apiary.id.in_(session_in.linked_apiary_ids)).all()
    elif session_in.scope_type == "LOCATION":
        locations = db.query(Location).filter(Location.id.in_(session_in.linked_location_ids)).all()
    elif session_in.scope_type == "HIVE":
        hives = db.query(Hive).filter(Hive.id.in_(session_in.linked_hive_ids)).all()

    new_session = LogSession(
        title=session_in.title,
        scope_type=session_in.scope_type,
        hive_id=session_in.hive_id,
        apiary_id=apiary_id,
        created_by_id=current_user.id,
        linked_apiaries=apiaries,
        linked_locations=locations,
        linked_hives=hives
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.put("/sessions/{session_id}", response_model=LogSessionOut)
def update_session(
    session_id: str,
    session_in: LogSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates session title or linked hive."""
    session = db.query(LogSession).filter(LogSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    check_access(session.apiary_id, current_user, db)
    
    from app.models.apiary import Apiary
    from app.models.location import Location

    apiaries = []
    locations = []
    hives = []
    
    if session_in.scope_type == "APIARY":
        apiaries = db.query(Apiary).filter(Apiary.id.in_(session_in.linked_apiary_ids)).all()
    elif session_in.scope_type == "LOCATION":
        locations = db.query(Location).filter(Location.id.in_(session_in.linked_location_ids)).all()
    elif session_in.scope_type == "HIVE":
        hives = db.query(Hive).filter(Hive.id.in_(session_in.linked_hive_ids)).all()

    session.title = session_in.title
    session.scope_type = session_in.scope_type
    session.hive_id = session_in.hive_id
    session.linked_apiaries = apiaries
    session.linked_locations = locations
    session.linked_hives = hives
    
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes session and all its nested logs (cascading)."""
    session = db.query(LogSession).filter(LogSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    check_access(session.apiary_id, current_user, db, require_admin=True)
    
    # Delete linked images from filesystem before deleting the session
    for entry in session.entries:
        for img in entry.images:
            for path in [img.image_path, img.thumbnail_path]:
                if path:
                    full_p = os.path.join(settings.UPLOAD_DIR, path)
                    if os.path.exists(full_p):
                        try:
                            os.remove(full_p)
                        except Exception:
                            pass
                            
    db.delete(session)
    db.commit()
    return

# -----------------
# ENTRIES ENDPOINTS
# -----------------

@router.get("/entries", response_model=List[LogEntryOut])
def list_entries(
    apiary_id: Optional[str] = Query(None, description="Scope search to a specific apiary"),
    hive_id: Optional[str] = Query(None, description="Filter by hive"),
    session_id: Optional[str] = Query(None, description="Filter by session"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists entries with optional hive, session, or apiary filtering, ordered by date desc."""
    if apiary_id:
        check_access(apiary_id, current_user, db)
        query = db.query(LogEntry).filter(LogEntry.apiary_id == apiary_id)
    else:
        if current_user.role == "SYSTEM_ADMIN":
            query = db.query(LogEntry)
        else:
            from app.models.apiary import Apiary, ApiaryMembership
            authorized_apiary_ids = [
                a.id for a in db.query(Apiary).join(ApiaryMembership).filter(
                    ApiaryMembership.user_id == current_user.id
                ).all()
            ]
            query = db.query(LogEntry).filter(LogEntry.apiary_id.in_(authorized_apiary_ids))

    query = query.options(
        joinedload(LogEntry.created_by),
        joinedload(LogEntry.apiary),
        joinedload(LogEntry.hive).joinedload(Hive.location),
            joinedload(LogEntry.inspection_detail).joinedload(InspectionDetail.boxes),
        joinedload(LogEntry.varroa_count_detail),
        joinedload(LogEntry.varroa_treatment_detail),
        joinedload(LogEntry.images)
    )
    
    if hive_id:
        query = query.filter(LogEntry.hive_id == hive_id)
    if session_id:
        query = query.filter(LogEntry.session_id == session_id)
        
    return query.order_by(LogEntry.date.desc(), LogEntry.created_at.desc()).all()

@router.post("/entries", response_model=LogEntryOut, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry_in: LogEntryCreate,
    apiary_id: str = Query(..., description="Scope creation to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a log entry, including nested inspection details, varroa counts, or treatments."""
    check_access(apiary_id, current_user, db)
    
    # Verify hive exists and belongs to the active apiary
    hive = db.query(Hive).options(
        joinedload(Hive.boxes).joinedload(HiveBox.frame_type),
        joinedload(Hive.frame_type)
    ).filter(Hive.id == entry_in.hive_id, Hive.apiary_id == apiary_id).first()
    if not hive:
        raise HTTPException(status_code=400, detail="Bienenvolk gehört nicht zu dieser Imkerei oder existiert nicht")

    new_entry = LogEntry(
        hive_id=entry_in.hive_id,
        session_id=entry_in.session_id,
        date=entry_in.date,
        entry_type=entry_in.entry_type,
        notes=entry_in.notes,
        apiary_id=apiary_id,
        created_by_id=current_user.id
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    # 1. Inspection details (box-based)
    if entry_in.entry_type == "INSPECTION" and entry_in.inspection_detail:
        detail = InspectionDetail(log_entry_id=new_entry.id)
        db.add(detail)
        db.commit()
        db.refresh(detail)

        for box_in in entry_in.inspection_detail.boxes:
            box = InspectionBox(
                inspection_id=detail.id,
                box_index=box_in.box_index,
                brood_total=box_in.brood_total,
                food_total=box_in.food_total,
                bee_total=box_in.bee_total,
                drone_total=box_in.drone_total,
                drone_brood_total=box_in.drone_brood_total,
                pollen_total=box_in.pollen_total,
                brood_eighths=box_in.brood_eighths,
                food_eighths=box_in.food_eighths,
                bee_eighths=box_in.bee_eighths,
                drone_eighths=box_in.drone_eighths,
                drone_brood_eighths=box_in.drone_brood_eighths,
                pollen_eighths=box_in.pollen_eighths,
            )
            db.add(box)
        db.commit()

    # 2. Varroa counts
    elif entry_in.entry_type == "VARROA_COUNT" and entry_in.varroa_count_detail:
        season, estimated = estimate_varroa(entry_in.varroa_count_detail.raw_count, entry_in.date, db)
        detail = VarroaCountDetail(
            log_entry_id=new_entry.id,
            raw_count=entry_in.varroa_count_detail.raw_count,
            season=season,
            estimated_total=estimated
        )
        db.add(detail)
        db.commit()

    # 3. Varroa treatments
    elif entry_in.entry_type == "VARROA_TREATMENT" and entry_in.varroa_treatment_detail:
        detail = VarroaTreatmentDetail(
            log_entry_id=new_entry.id,
            product=entry_in.varroa_treatment_detail.product,
            dosage=entry_in.varroa_treatment_detail.dosage,
            treatment_notes=entry_in.varroa_treatment_detail.treatment_notes
        )
        db.add(detail)
        db.commit()

    # Refresh session update time if linked
    if entry_in.session_id:
        session = db.query(LogSession).filter(LogSession.id == entry_in.session_id).first()
        if session:
            db.commit() # Trigger timestamps updates
            
    db.refresh(new_entry)
    return new_entry

@router.put("/entries/{entry_id}", response_model=LogEntryOut)
def update_entry(
    entry_id: str,
    entry_in: LogEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates log entry notes and overwrites nested details (inspections, varroa, treatment)."""
    entry = db.query(LogEntry).filter(LogEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Logbuch-Eintrag nicht gefunden")
    
    check_access(entry.apiary_id, current_user, db)

    entry.date = entry_in.date
    entry.notes = entry_in.notes
    entry.session_id = entry_in.session_id
    
    # 1. Update Inspection details (box-based)
    if entry.entry_type == "INSPECTION":
        # Delete old boxes & detail if we need to recreate, or overwrite
        if entry.inspection_detail:
            db.query(InspectionBox).filter(InspectionBox.inspection_id == entry.inspection_detail.id).delete()
            db.delete(entry.inspection_detail)
            db.commit()

        if entry_in.inspection_detail:
            detail = InspectionDetail(log_entry_id=entry.id)
            db.add(detail)
            db.commit()
            db.refresh(detail)

            for box_in in entry_in.inspection_detail.boxes:
                box = InspectionBox(
                    inspection_id=detail.id,
                    box_index=box_in.box_index,
                    brood_total=box_in.brood_total,
                    food_total=box_in.food_total,
                    bee_total=box_in.bee_total,
                    drone_total=box_in.drone_total,
                    drone_brood_total=box_in.drone_brood_total,
                    pollen_total=box_in.pollen_total,
                    brood_eighths=box_in.brood_eighths,
                    food_eighths=box_in.food_eighths,
                    bee_eighths=box_in.bee_eighths,
                    drone_eighths=box_in.drone_eighths,
                    drone_brood_eighths=box_in.drone_brood_eighths,
                    pollen_eighths=box_in.pollen_eighths,
                )
                db.add(box)
            db.commit()

    # 2. Update Varroa counts
    elif entry.entry_type == "VARROA_COUNT":
        if entry.varroa_count_detail:
            db.delete(entry.varroa_count_detail)
            db.commit()
            
        if entry_in.varroa_count_detail:
            season, estimated = estimate_varroa(entry_in.varroa_count_detail.raw_count, entry_in.date, db)
            detail = VarroaCountDetail(
                log_entry_id=entry.id,
                raw_count=entry_in.varroa_count_detail.raw_count,
                season=season,
                estimated_total=estimated
            )
            db.add(detail)
            db.commit()

    # 3. Update Varroa treatments
    elif entry.entry_type == "VARROA_TREATMENT":
        if entry.varroa_treatment_detail:
            db.delete(entry.varroa_treatment_detail)
            db.commit()
            
        if entry_in.varroa_treatment_detail:
            detail = VarroaTreatmentDetail(
                log_entry_id=entry.id,
                product=entry_in.varroa_treatment_detail.product,
                dosage=entry_in.varroa_treatment_detail.dosage,
                treatment_notes=entry_in.varroa_treatment_detail.treatment_notes
            )
            db.add(detail)
            db.commit()

    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a log entry, cascaded deletes remove related detail tables. Files are deleted from disk."""
    entry = db.query(LogEntry).filter(LogEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Logbuch-Eintrag nicht gefunden")
    
    check_access(entry.apiary_id, current_user, db, require_admin=True)

    # Clean files from disk
    for img in entry.images:
        for path in [img.image_path, img.thumbnail_path]:
            if path:
                full_p = os.path.join(settings.UPLOAD_DIR, path)
                if os.path.exists(full_p):
                    try:
                        os.remove(full_p)
                    except Exception:
                        pass

    db.delete(entry)
    db.commit()
    return

# -----------------
# IMAGES ENDPOINTS
# -----------------

@router.post("/entries/{entry_id}/images", response_model=LogEntryImageOut, status_code=status.HTTP_201_CREATED)
def upload_entry_image(
    entry_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads an image for the log entry, generates a 240x240 thumbnail, and validates maximum images limit (5)."""
    entry = db.query(LogEntry).filter(LogEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Logbuch-Eintrag nicht gefunden")
    
    check_access(entry.apiary_id, current_user, db)

    # Enforce limit of 5 images per entry
    if len(entry.images) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximale Anzahl von 5 Bildern pro Log-Eintrag erreicht"
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dateiformat nicht unterstützt (nur JPG, PNG, WEBP)"
        )

    file_uuid = uuid.uuid4().hex
    relative_img_path = f"logbook/images/{file_uuid}{ext}"
    relative_thumb_path = f"logbook/thumbnails/{file_uuid}.jpg"

    full_img_path = os.path.join(settings.UPLOAD_DIR, relative_img_path)
    full_thumb_path = os.path.join(settings.UPLOAD_DIR, relative_thumb_path)

    # Ensure directories exist
    os.makedirs(os.path.dirname(full_img_path), exist_ok=True)
    os.makedirs(os.path.dirname(full_thumb_path), exist_ok=True)

    # Save original image to disk
    file_bytes = file.file.read()
    with open(full_img_path, "wb") as buffer:
        buffer.write(file_bytes)

    # Generate thumbnail using Pillow
    try:
        with Image.open(full_img_path) as source:
            thumbnail_image = source.copy()
            thumbnail_image.thumbnail((240, 240))
            if thumbnail_image.mode not in ("RGB", "L"):
                thumbnail_image = thumbnail_image.convert("RGB")
            thumbnail_image.save(full_thumb_path, format="JPEG", quality=82)
    except Exception as e:
        # Fallback if Pillow fails: just save full image as thumbnail path too or keep null
        relative_thumb_path = None

    # Record in database
    new_image = LogEntryImage(
        log_entry_id=entry_id,
        image_path=relative_img_path,
        thumbnail_path=relative_thumb_path
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image

@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes an uploaded logbook image from database and local hard drive."""
    img = db.query(LogEntryImage).filter(LogEntryImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    
    # Check permissions on parent entry
    check_access(img.log_entry.apiary_id, current_user, db)

    # Delete physical files
    for path in [img.image_path, img.thumbnail_path]:
        if path:
            full_p = os.path.join(settings.UPLOAD_DIR, path)
            if os.path.exists(full_p):
                try:
                    os.remove(full_p)
                except Exception:
                    pass

    db.delete(img)
    db.commit()
    return
