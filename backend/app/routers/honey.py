from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import csv
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.honey_batch import HoneyBatch
from app.schemas.honey import HoneyBatchCreate, HoneyBatchUpdate, HoneyBatchOut
from app.routers.apiaries import check_access

router = APIRouter(prefix="/honey-batches", tags=["honey-batches"])

@router.get("", response_model=List[HoneyBatchOut])
def list_honey_batches(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all honey batches inside an authorized apiary."""
    check_access(apiary_id, current_user, db)
    return db.query(HoneyBatch).filter(HoneyBatch.apiary_id == apiary_id).order_by(HoneyBatch.harvest_date.desc()).all()

@router.post("", response_model=HoneyBatchOut, status_code=status.HTTP_201_CREATED)
def create_honey_batch(
    batch_in: HoneyBatchCreate,
    apiary_id: str = Query(..., description="Scope creation to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new honey batch."""
    check_access(apiary_id, current_user, db)

    new_batch = HoneyBatch(
        batch_number=batch_in.batch_number,
        honey_type=batch_in.honey_type,
        harvest_date=batch_in.harvest_date,
        bottling_date=batch_in.bottling_date,
        quantity_kg=batch_in.quantity_kg,
        water_content_percent=batch_in.water_content_percent,
        heating_temperature_celsius=batch_in.heating_temperature_celsius,
        best_before_date=batch_in.best_before_date,
        is_exact_date=batch_in.is_exact_date,
        dib_label_start=batch_in.dib_label_start,
        dib_label_end=batch_in.dib_label_end,
        reserve_sample_taken=batch_in.reserve_sample_taken,
        reserve_sample_date=batch_in.reserve_sample_date,
        reserve_sample_id=batch_in.reserve_sample_id,
        notes=batch_in.notes,
        apiary_id=apiary_id,
        created_by_id=current_user.id
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch

@router.get("/{batch_id}", response_model=HoneyBatchOut)
def get_honey_batch(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves a single honey batch by ID."""
    batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
    
    check_access(batch.apiary_id, current_user, db)
    return batch

@router.put("/{batch_id}", response_model=HoneyBatchOut)
def update_honey_batch(
    batch_id: str,
    batch_in: HoneyBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates general metadata of a honey batch."""
    batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
    
    check_access(batch.apiary_id, current_user, db)

    # Validate if fields are updated in a way that violates constraints
    is_exact = batch_in.is_exact_date if batch_in.is_exact_date is not None else batch.is_exact_date
    batch_num = batch_in.batch_number if batch_in.batch_number is not None else batch.batch_number
    if not is_exact and (not batch_num or not batch_num.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Die Los-Nr. (batch_number) ist zwingend erforderlich, wenn das MHD nicht taggenau angegeben ist."
        )

    for field, value in batch_in.model_dump(exclude_unset=True).items():
        setattr(batch, field, value)

    db.commit()
    db.refresh(batch)
    return batch

@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_honey_batch(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a honey batch."""
    batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
    
    check_access(batch.apiary_id, current_user, db)
    db.delete(batch)
    db.commit()
    return

@router.get("/export/csv")
def export_honey_book_csv(
    apiary_id: str = Query(..., description="Scope export to a specific apiary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports the Honigbuch (Honey Book) for an apiary to CSV."""
    check_access(apiary_id, current_user, db)
    batches = db.query(HoneyBatch).filter(HoneyBatch.apiary_id == apiary_id).order_by(HoneyBatch.harvest_date.desc()).all()

    # Generate CSV in memory with utf-8-sig BOM for Excel compatibility
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')

    # Headers
    writer.writerow([
        "Los-Nr. / Chargen-Nr.",
        "Honigsorte",
        "Erntedatum",
        "Abfülldatum",
        "Menge (kg)",
        "Wassergehalt (%)",
        "Erwärmungstemp. (°C)",
        "Mindesthaltbarkeitsdatum (MHD)",
        "MHD Taggenau",
        "D.I.B. Gewährverschluss Start",
        "D.I.B. Gewährverschluss Ende",
        "Rückstellprobe vorhanden",
        "Rückstellprobe Datum",
        "Rückstellprobe ID",
        "Notizen"
    ])

    for b in batches:
        writer.writerow([
            b.batch_number or "MHD-Ausnahme",
            b.honey_type,
            b.harvest_date.strftime("%d.%m.%Y") if b.harvest_date else "",
            b.bottling_date.strftime("%d.%m.%Y") if b.bottling_date else "",
            str(b.quantity_kg).replace('.', ','),
            str(b.water_content_percent).replace('.', ',') if b.water_content_percent is not None else "",
            str(b.heating_temperature_celsius).replace('.', ',') if b.heating_temperature_celsius is not None else "",
            b.best_before_date.strftime("%d.%m.%Y") if b.best_before_date else "",
            "Ja" if b.is_exact_date else "Nein",
            b.dib_label_start or "",
            b.dib_label_end or "",
            "Ja" if b.reserve_sample_taken else "Nein",
            b.reserve_sample_date.strftime("%d.%m.%Y") if b.reserve_sample_date else "",
            b.reserve_sample_id or "",
            b.notes or ""
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"honigbuch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.BytesIO(csv_data.encode("utf-8")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
