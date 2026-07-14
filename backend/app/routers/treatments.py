from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List, Optional
import os
import uuid
import csv
import io
from PIL import Image

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.hive import Hive
from app.models.treatment import TreatmentMethod, Treatment, TreatmentImage, TreatmentApplicationType
from app.schemas.treatment import (
    TreatmentMethodOut, TreatmentOut, TreatmentCreate, TreatmentUpdate, TreatmentImageOut,
    TreatmentApplicationTypeOut
)
from app.routers.apiaries import check_access

router = APIRouter(prefix="/treatments", tags=["treatments"])


@router.get("/methods", response_model=List[TreatmentMethodOut])
def list_active_methods(db: Session = Depends(get_db)):
    """Lists all active treatment methods (for beekeepers to select in dropdown)."""
    return db.query(TreatmentMethod).filter(TreatmentMethod.is_active == True).order_by(TreatmentMethod.name).all()


@router.get("/application-types", response_model=List[TreatmentApplicationTypeOut])
def list_active_application_types(db: Session = Depends(get_db)):
    """Lists all active treatment application types (for beekeepers to select in dropdown)."""
    return db.query(TreatmentApplicationType).filter(TreatmentApplicationType.is_active == True).order_by(TreatmentApplicationType.name).all()


@router.get("/export/csv")
def export_treatments_csv(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    hive_id: Optional[str] = Query(None, description="Filter by a specific hive"),
    location_id: Optional[str] = Query(None, description="Filter by a specific location"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports treatments in the apiary to CSV (filtered)."""
    check_access(apiary_id, current_user, db)

    query = db.query(Treatment).join(Hive).filter(Treatment.apiary_id == apiary_id)

    if hive_id:
        query = query.filter(Treatment.hive_id == hive_id)
    if location_id:
        query = query.filter(Hive.location_id == location_id)
    if start_date:
        query = query.filter(Treatment.date >= start_date)
    if end_date:
        query = query.filter(Treatment.date <= end_date)

    treatments = query.options(
        joinedload(Treatment.treatment_method),
        joinedload(Treatment.application_type),
        joinedload(Treatment.hive).joinedload(Hive.location)
    ).order_by(Treatment.date.desc()).all()

    # Generate CSV in memory with utf-8-sig BOM for Excel compatibility
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')

    # Headers
    writer.writerow([
        "Datum",
        "Volk",
        "Standort",
        "Behandlungsmethode",
        "Menge",
        "Einheit",
        "Applikationsmethode",
        "Notizen"
    ])

    for t in treatments:
        writer.writerow([
            t.date.strftime("%Y-%m-%d") if t.date else "",
            t.hive.name if t.hive else "",
            t.hive.location.name if t.hive and t.hive.location else "",
            t.treatment_method.name if t.treatment_method else "",
            t.amount,
            t.treatment_method.unit if t.treatment_method else "",
            t.application_type.name if t.application_type else "",
            t.notes or ""
        ])

    output.seek(0)
    response_data = output.getvalue().encode('utf-8-sig')
    
    return StreamingResponse(
        io.BytesIO(response_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=behandlungen_{date.today().strftime('%Y-%m-%d')}.csv"}
    )


@router.get("", response_model=List[TreatmentOut])
def list_treatments(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    hive_id: Optional[str] = Query(None, description="Filter by a specific hive"),
    location_id: Optional[str] = Query(None, description="Filter by a specific location"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all treatments in the apiary with optional filters."""
    check_access(apiary_id, current_user, db)

    query = db.query(Treatment).join(Hive).filter(Treatment.apiary_id == apiary_id)

    if hive_id:
        query = query.filter(Treatment.hive_id == hive_id)
    if location_id:
        query = query.filter(Hive.location_id == location_id)
    if start_date:
        query = query.filter(Treatment.date >= start_date)
    if end_date:
        query = query.filter(Treatment.date <= end_date)

    return query.options(
        joinedload(Treatment.treatment_method),
        joinedload(Treatment.application_type),
        joinedload(Treatment.hive).joinedload(Hive.location),
        joinedload(Treatment.images)
    ).order_by(Treatment.date.desc()).all()


@router.post("", response_model=TreatmentOut, status_code=status.HTTP_201_CREATED)
def create_treatment(
    treatment_in: TreatmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new treatment entry for a hive."""
    hive = db.query(Hive).filter(Hive.id == treatment_in.hive_id).first()
    if not hive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bienenvolk nicht gefunden."
        )

    # Validate user access to the hive's apiary
    check_access(hive.apiary_id, current_user, db)

    method = db.query(TreatmentMethod).filter(TreatmentMethod.id == treatment_in.treatment_method_id).first()
    if not method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ausgewählte Behandlungsmethode existiert nicht."
        )

    if treatment_in.application_type_id:
        app_type = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.id == treatment_in.application_type_id).first()
        if not app_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ausgewählte Applikationsmethode existiert nicht."
            )

    new_treatment = Treatment(
        hive_id=treatment_in.hive_id,
        treatment_method_id=treatment_in.treatment_method_id,
        application_type_id=treatment_in.application_type_id,
        date=treatment_in.date,
        amount=treatment_in.amount,
        notes=treatment_in.notes,
        apiary_id=hive.apiary_id,
        created_by_id=current_user.id
    )
    db.add(new_treatment)
    db.commit()
    db.refresh(new_treatment)

    # Re-query with relations loaded
    return db.query(Treatment).options(
        joinedload(Treatment.treatment_method),
        joinedload(Treatment.application_type),
        joinedload(Treatment.hive).joinedload(Hive.location),
        joinedload(Treatment.images)
    ).filter(Treatment.id == new_treatment.id).first()


@router.put("/{treatment_id}", response_model=TreatmentOut)
def update_treatment(
    treatment_id: str,
    treatment_in: TreatmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates a treatment entry."""
    treatment = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not treatment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behandlungseintrag nicht gefunden."
        )

    # Validate access to the treatment's apiary
    check_access(treatment.apiary_id, current_user, db)

    if treatment_in.hive_id is not None and treatment_in.hive_id != treatment.hive_id:
        new_hive = db.query(Hive).filter(Hive.id == treatment_in.hive_id).first()
        if not new_hive or new_hive.apiary_id != treatment.apiary_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiges Bienenvolk ausgewählt."
            )
        treatment.hive_id = treatment_in.hive_id

    if treatment_in.treatment_method_id is not None:
        method = db.query(TreatmentMethod).filter(TreatmentMethod.id == treatment_in.treatment_method_id).first()
        if not method:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ausgewählte Behandlungsmethode existiert nicht."
            )
        treatment.treatment_method_id = treatment_in.treatment_method_id

    if treatment_in.application_type_id is not None:
        if treatment_in.application_type_id:
            app_type = db.query(TreatmentApplicationType).filter(TreatmentApplicationType.id == treatment_in.application_type_id).first()
            if not app_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ausgewählte Applikationsmethode existiert nicht."
                )
            treatment.application_type_id = treatment_in.application_type_id
        else:
            treatment.application_type_id = None

    if treatment_in.date is not None:
        treatment.date = treatment_in.date
    if treatment_in.amount is not None:
        treatment.amount = treatment_in.amount
    if treatment_in.notes is not None:
        treatment.notes = treatment_in.notes

    db.commit()
    db.refresh(treatment)

    return db.query(Treatment).options(
        joinedload(Treatment.treatment_method),
        joinedload(Treatment.application_type),
        joinedload(Treatment.hive).joinedload(Hive.location),
        joinedload(Treatment.images)
    ).filter(Treatment.id == treatment.id).first()


@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_treatment(
    treatment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a treatment entry and all its images from the disk."""
    treatment = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not treatment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behandlungseintrag nicht gefunden."
        )

    # Validate access (requires admin access to the apiary to delete logs)
    check_access(treatment.apiary_id, current_user, db, require_admin=True)

    # Delete physically stored files
    for img in treatment.images:
        for path in [img.image_path, img.thumbnail_path]:
            if path:
                full_path = os.path.join(settings.UPLOAD_DIR, path)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception:
                        pass

    db.delete(treatment)
    db.commit()
    return


@router.post("/{treatment_id}/images", response_model=TreatmentImageOut, status_code=status.HTTP_201_CREATED)
def upload_treatment_image(
    treatment_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads an image for the treatment entry, generates a 240x240 thumbnail, and validates maximum limit of 5."""
    treatment = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not treatment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behandlungseintrag nicht gefunden."
        )

    check_access(treatment.apiary_id, current_user, db)

    # Validate limit of 5 images
    if len(treatment.images) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximale Anzahl von 5 Bildern pro Behandlungseintrag erreicht."
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dateiformat nicht unterstützt (nur JPG, PNG, WEBP)."
        )

    file_uuid = uuid.uuid4().hex
    relative_img_path = f"treatments/images/{file_uuid}{ext}"
    relative_thumb_path = f"treatments/thumbnails/{file_uuid}.jpg"

    full_img_path = os.path.join(settings.UPLOAD_DIR, relative_img_path)
    full_thumb_path = os.path.join(settings.UPLOAD_DIR, relative_thumb_path)

    # Ensure target directories exist
    os.makedirs(os.path.dirname(full_img_path), exist_ok=True)
    os.makedirs(os.path.dirname(full_thumb_path), exist_ok=True)

    # Save original image to disk
    file_bytes = file.file.read()
    with open(full_img_path, "wb") as buffer:
        buffer.write(file_bytes)

    # Generate thumbnail
    try:
        with Image.open(full_img_path) as source:
            thumbnail_image = source.copy()
            thumbnail_image.thumbnail((240, 240))
            if thumbnail_image.mode not in ("RGB", "L"):
                thumbnail_image = thumbnail_image.convert("RGB")
            thumbnail_image.save(full_thumb_path, format="JPEG", quality=82)
    except Exception:
        relative_thumb_path = None

    # Save in DB
    new_image = TreatmentImage(
        treatment_id=treatment_id,
        image_path=relative_img_path,
        thumbnail_path=relative_thumb_path
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_treatment_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes an uploaded treatment image from database and local disk."""
    img = db.query(TreatmentImage).filter(TreatmentImage.id == image_id).first()
    if not img:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bild nicht gefunden."
        )

    check_access(img.treatment.apiary_id, current_user, db)

    # Delete physical files
    for path in [img.image_path, img.thumbnail_path]:
        if path:
            full_path = os.path.join(settings.UPLOAD_DIR, path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception:
                    pass

    db.delete(img)
    db.commit()
    return
