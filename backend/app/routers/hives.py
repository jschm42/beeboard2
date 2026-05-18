from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.hive import Hive, HiveBox
from app.models.administration import FrameType, VarroaMultiplier
from app.schemas.hive import HiveCreate, HiveOut, HiveBoxCreate, HiveBoxOut
from app.schemas.admin import FrameTypeOut, VarroaMultiplierOut
from app.routers.apiaries import check_access

router = APIRouter(prefix="/hives", tags=["hives"])

@router.get("/frame-types", response_model=List[FrameTypeOut])
def list_frame_types(db: Session = Depends(get_db)):
    """Lists all available FrameType master data."""
    return db.query(FrameType).order_by(FrameType.name).all()

@router.get("/varroa-multipliers", response_model=List[VarroaMultiplierOut])
def list_varroa_multipliers(db: Session = Depends(get_db)):
    """Lists all season multipliers."""
    return db.query(VarroaMultiplier).order_by(VarroaMultiplier.season).all()

@router.get("", response_model=List[HiveOut])
def list_hives(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all hives inside an authorized apiary, including their boxes."""
    check_access(apiary_id, current_user, db)
    return db.query(Hive).filter(Hive.apiary_id == apiary_id).order_by(Hive.name).all()

@router.post("", response_model=HiveOut, status_code=status.HTTP_201_CREATED)
def create_hive(
    hive_in: HiveCreate,
    apiary_id: str = Query(..., description="Scope creation to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new hive. If boxes are supplied in the body, configures them nestedly."""
    check_access(apiary_id, current_user, db)

    new_hive = Hive(
        name=hive_in.name,
        location_id=hive_in.location_id,
        frame_type_id=hive_in.frame_type_id,
        queen_year=hive_in.queen_year,
        is_active=hive_in.is_active,
        notes=hive_in.notes,
        apiary_id=apiary_id,
        created_by_id=current_user.id
    )
    db.add(new_hive)
    db.commit()
    db.refresh(new_hive)

    # Nest boxes creation
    if hive_in.boxes:
        for box_in in hive_in.boxes:
            new_box = HiveBox(
                hive_id=new_hive.id,
                order=box_in.order,
                frame_type_id=box_in.frame_type_id,
                frame_count=box_in.frame_count,
                box_type=box_in.box_type
            )
            db.add(new_box)
        db.commit()
        db.refresh(new_hive)

    return new_hive

@router.get("/{hive_id}", response_model=HiveOut)
def get_hive(
    hive_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves a single hive by ID after checking apiary access permissions."""
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bienenvolk nicht gefunden")
    
    check_access(hive.apiary_id, current_user, db)
    return hive

@router.put("/{hive_id}", response_model=HiveOut)
def update_hive(
    hive_id: str,
    hive_in: HiveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates general metadata of a hive (name, location, notes, active status)."""
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bienenvolk nicht gefunden")
    
    check_access(hive.apiary_id, current_user, db)

    hive.name = hive_in.name
    hive.location_id = hive_in.location_id
    hive.frame_type_id = hive_in.frame_type_id
    hive.queen_year = hive_in.queen_year
    hive.is_active = hive_in.is_active
    hive.notes = hive_in.notes
    
    db.commit()
    db.refresh(hive)
    return hive

@router.delete("/{hive_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hive(
    hive_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a hive, cascaded delete-orphan triggers remove boxes and logbook records."""
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bienenvolk nicht gefunden")
    
    check_access(hive.apiary_id, current_user, db, require_admin=True)
    
    # Delete image from disk if exists
    if hive.image_path:
        full_path = os.path.join(settings.UPLOAD_DIR, hive.image_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception:
                pass

    db.delete(hive)
    db.commit()
    return

@router.post("/{hive_id}/boxes", response_model=List[HiveBoxOut])
def configure_boxes(
    hive_id: str,
    boxes_in: List[HiveBoxCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reconfigures the boxes of a hive. Deletes old, inserts new in a atomic operation."""
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bienenvolk nicht gefunden")
    
    check_access(hive.apiary_id, current_user, db)

    # Delete existing boxes
    db.query(HiveBox).filter(HiveBox.hive_id == hive_id).delete()

    # Re-insert boxes
    new_boxes = []
    for box in boxes_in:
        new_box = HiveBox(
            hive_id=hive_id,
            order=box.order,
            frame_type_id=box.frame_type_id,
            frame_count=box.frame_count,
            box_type=box.box_type
        )
        db.add(new_box)
        new_boxes.append(new_box)

    db.commit()
    # Refresh to load frame relationships
    for box in new_boxes:
        db.refresh(box)
        
    return new_boxes

@router.post("/{hive_id}/photo", response_model=HiveOut)
def upload_hive_photo(
    hive_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads a profile photo for the hive."""
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bienenvolk nicht gefunden")
    
    check_access(hive.apiary_id, current_user, db)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dateiformat nicht unterstützt (nur JPG, PNG, WEBP)")

    # Save to disk
    relative_path = f"hives/photos/{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, relative_path)
    
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Delete old photo if it exists
    if hive.image_path:
        old_full_path = os.path.join(settings.UPLOAD_DIR, hive.image_path)
        if os.path.exists(old_full_path):
            try:
                os.remove(old_full_path)
            except Exception:
                pass

    hive.image_path = relative_path
    db.commit()
    db.refresh(hive)
    return hive
