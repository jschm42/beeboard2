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
from app.models.honey_batch import HoneyBatch, HoneyBatchDIBRange, HoneyBottling, HoneyBottlingDIBRange
from app.schemas.honey import (
    HoneyBatchCreate, HoneyBatchUpdate, HoneyBatchOut,
    HoneyBottlingCreate, HoneyBottlingUpdate, HoneyBottlingOut
)
from app.routers.apiaries import check_access
from app.models.administration import NumberRange

def check_and_increment_range(db: Session, key: str, value: str):
    range_obj = db.query(NumberRange).filter(NumberRange.key == key, NumberRange.is_active == True).first()
    if range_obj:
        expected_value = f"{range_obj.prefix or ''}{range_obj.current_value:0{range_obj.digits}d}"
        if value == expected_value:
            range_obj.current_value += 1
            db.add(range_obj)

router = APIRouter(prefix="/honey-batches", tags=["honey-batches"])

@router.get("/suggest-number")
def suggest_number(
    key: str = Query(..., description="Key of the number range: batch_number or reserve_sample_id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Suggests the next number for the given number range key."""
    range_obj = db.query(NumberRange).filter(NumberRange.key == key, NumberRange.is_active == True).first()
    if not range_obj:
        return {"suggested_value": ""}
    
    formatted_value = f"{range_obj.prefix or ''}{range_obj.current_value:0{range_obj.digits}d}"
    return {"suggested_value": formatted_value}

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

    # Validate duplicates
    if batch_in.batch_number:
        existing = db.query(HoneyBatch).filter(HoneyBatch.batch_number == batch_in.batch_number).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Diese Los-/Chargennummer wird bereits verwendet.")

    if batch_in.reserve_sample_taken and batch_in.reserve_sample_id:
        existing_sample = db.query(HoneyBatch).filter(HoneyBatch.reserve_sample_id == batch_in.reserve_sample_id).first()
        if existing_sample:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Diese Rückstellproben-ID wird bereits verwendet.")

    # Increment ranges if the values match expected suggestions
    if batch_in.batch_number:
        check_and_increment_range(db, "batch_number", batch_in.batch_number)
    
    if batch_in.reserve_sample_taken and batch_in.reserve_sample_id:
        check_and_increment_range(db, "reserve_sample_id", batch_in.reserve_sample_id)

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
        reserve_sample_taken=batch_in.reserve_sample_taken,
        reserve_sample_date=batch_in.reserve_sample_date,
        reserve_sample_id=batch_in.reserve_sample_id,
        notes=batch_in.notes,
        apiary_id=apiary_id,
        created_by_id=current_user.id
    )

    # Process initial bottlings if provided
    bottlings_to_create = []
    if batch_in.bottlings:
        for b in batch_in.bottlings:
            bottling_obj = HoneyBottling(
                bottling_date=b.bottling_date,
                jar_size_g=b.jar_size_g,
                quantity_jars=b.quantity_jars,
                quantity_kg=b.quantity_kg,
                notes=b.notes
            )
            # DIB ranges for bottling
            ranges_to_create = []
            if b.dib_ranges:
                for r in b.dib_ranges:
                    if r.dib_label_start or r.dib_label_end:
                        ranges_to_create.append(
                            HoneyBottlingDIBRange(
                                dib_label_start=r.dib_label_start,
                                dib_label_end=r.dib_label_end
                            )
                        )
            elif b.dib_label_start or b.dib_label_end:
                ranges_to_create.append(
                    HoneyBottlingDIBRange(
                        dib_label_start=b.dib_label_start,
                        dib_label_end=b.dib_label_end
                    )
                )
            bottling_obj.dib_ranges = ranges_to_create
            bottlings_to_create.append(bottling_obj)
    elif batch_in.bottling_date or batch_in.dib_ranges or batch_in.dib_label_start or batch_in.dib_label_end:
        # Backward compatibility for single bottling input in batch creation
        b_date = batch_in.bottling_date or batch_in.harvest_date
        bottling_obj = HoneyBottling(
            bottling_date=b_date,
            jar_size_g=None,
            quantity_jars=None,
            quantity_kg=batch_in.quantity_kg,
            notes=None
        )
        ranges_to_create = []
        if batch_in.dib_ranges:
            for r in batch_in.dib_ranges:
                if r.dib_label_start or r.dib_label_end:
                    ranges_to_create.append(
                        HoneyBottlingDIBRange(
                            dib_label_start=r.dib_label_start,
                            dib_label_end=r.dib_label_end
                        )
                    )
        elif batch_in.dib_label_start or batch_in.dib_label_end:
            ranges_to_create.append(
                HoneyBottlingDIBRange(
                    dib_label_start=batch_in.dib_label_start,
                    dib_label_end=batch_in.dib_label_end
                )
            )
        bottling_obj.dib_ranges = ranges_to_create
        bottlings_to_create.append(bottling_obj)

    new_batch.bottlings = bottlings_to_create

    # Also keep legacy HoneyBatchDIBRange for backward compatibility if given
    legacy_dib = []
    if batch_in.dib_ranges:
        for r in batch_in.dib_ranges:
            if r.dib_label_start or r.dib_label_end:
                legacy_dib.append(
                    HoneyBatchDIBRange(
                        dib_label_start=r.dib_label_start,
                        dib_label_end=r.dib_label_end
                    )
                )
    elif batch_in.dib_label_start or batch_in.dib_label_end:
        legacy_dib.append(
            HoneyBatchDIBRange(
                dib_label_start=batch_in.dib_label_start,
                dib_label_end=batch_in.dib_label_end
            )
        )
    new_batch.dib_ranges = legacy_dib

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

    # Validate duplicates on update
    if batch_in.batch_number:
        existing = db.query(HoneyBatch).filter(
            HoneyBatch.batch_number == batch_in.batch_number,
            HoneyBatch.id != batch_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Diese Los-/Chargennummer wird bereits verwendet.")

    sample_taken = batch_in.reserve_sample_taken if batch_in.reserve_sample_taken is not None else batch.reserve_sample_taken
    sample_id = batch_in.reserve_sample_id if batch_in.reserve_sample_id is not None else batch.reserve_sample_id
    if sample_taken and sample_id:
        existing_sample = db.query(HoneyBatch).filter(
            HoneyBatch.reserve_sample_id == sample_id,
            HoneyBatch.id != batch_id
        ).first()
        if existing_sample:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Diese Rückstellproben-ID wird bereits verwendet.")

    # Increment ranges if the values match expected suggestions
    if batch_in.batch_number:
        check_and_increment_range(db, "batch_number", batch_in.batch_number)
    
    if sample_taken and batch_in.reserve_sample_id:
        check_and_increment_range(db, "reserve_sample_id", batch_in.reserve_sample_id)

    update_data = batch_in.model_dump(exclude_unset=True)

    # Handle legacy DIB ranges updates on batch level if provided
    if "dib_ranges" in update_data:
        db.query(HoneyBatchDIBRange).filter(HoneyBatchDIBRange.honey_batch_id == batch.id).delete()
        new_ranges = []
        if batch_in.dib_ranges is not None:
            for r in batch_in.dib_ranges:
                if r.dib_label_start or r.dib_label_end:
                    new_ranges.append(
                        HoneyBatchDIBRange(
                            honey_batch_id=batch.id,
                            dib_label_start=r.dib_label_start,
                            dib_label_end=r.dib_label_end
                        )
                    )
        batch.dib_ranges = new_ranges
        del update_data["dib_ranges"]
    elif "dib_label_start" in update_data or "dib_label_end" in update_data:
        start = batch_in.dib_label_start if "dib_label_start" in update_data else (batch.dib_ranges[0].dib_label_start if batch.dib_ranges else None)
        end = batch_in.dib_label_end if "dib_label_end" in update_data else (batch.dib_ranges[0].dib_label_end if batch.dib_ranges else None)
        
        db.query(HoneyBatchDIBRange).filter(HoneyBatchDIBRange.honey_batch_id == batch.id).delete()
        if start or end:
            batch.dib_ranges = [
                HoneyBatchDIBRange(
                    honey_batch_id=batch.id,
                    dib_label_start=start,
                    dib_label_end=end
                )
            ]
        else:
            batch.dib_ranges = []

    if "dib_label_start" in update_data:
        del update_data["dib_label_start"]
    if "dib_label_end" in update_data:
        del update_data["dib_label_end"]

    for field, value in update_data.items():
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


# --- Bottling Endpoints ---

@router.get("/{batch_id}/bottlings", response_model=List[HoneyBottlingOut])
def list_honey_bottlings(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all bottlings for a specific honey batch."""
    batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
    check_access(batch.apiary_id, current_user, db)
    return batch.bottlings


@router.post("/{batch_id}/bottlings", response_model=HoneyBottlingOut, status_code=status.HTTP_201_CREATED)
def create_honey_bottling(
    batch_id: str,
    bottling_in: HoneyBottlingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new bottling for a specific honey batch."""
    batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
    check_access(batch.apiary_id, current_user, db)

    bottling = HoneyBottling(
        honey_batch_id=batch.id,
        bottling_date=bottling_in.bottling_date,
        jar_size_g=bottling_in.jar_size_g,
        quantity_jars=bottling_in.quantity_jars,
        quantity_kg=bottling_in.quantity_kg,
        notes=bottling_in.notes
    )

    # Process DIB ranges
    dib_ranges_to_create = []
    if bottling_in.dib_ranges:
        for r in bottling_in.dib_ranges:
            if r.dib_label_start or r.dib_label_end:
                dib_ranges_to_create.append(
                    HoneyBottlingDIBRange(
                        dib_label_start=r.dib_label_start,
                        dib_label_end=r.dib_label_end
                    )
                )
    elif bottling_in.dib_label_start or bottling_in.dib_label_end:
        dib_ranges_to_create.append(
            HoneyBottlingDIBRange(
                dib_label_start=bottling_in.dib_label_start,
                dib_label_end=bottling_in.dib_label_end
            )
        )
    bottling.dib_ranges = dib_ranges_to_create

    db.add(bottling)
    db.commit()
    db.refresh(bottling)
    return bottling


@router.put("/{batch_id}/bottlings/{bottling_id}", response_model=HoneyBottlingOut)
def update_honey_bottling(
    batch_id: str,
    bottling_id: str,
    bottling_in: HoneyBottlingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates a bottling."""
    batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
    check_access(batch.apiary_id, current_user, db)

    bottling = db.query(HoneyBottling).filter(
        HoneyBottling.id == bottling_id,
        HoneyBottling.honey_batch_id == batch_id
    ).first()
    if not bottling:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abfüllung nicht gefunden")

    update_data = bottling_in.model_dump(exclude_unset=True)

    if "dib_ranges" in update_data:
        db.query(HoneyBottlingDIBRange).filter(HoneyBottlingDIBRange.bottling_id == bottling.id).delete()
        new_ranges = []
        if bottling_in.dib_ranges is not None:
            for r in bottling_in.dib_ranges:
                if r.dib_label_start or r.dib_label_end:
                    new_ranges.append(
                        HoneyBottlingDIBRange(
                            bottling_id=bottling.id,
                            dib_label_start=r.dib_label_start,
                            dib_label_end=r.dib_label_end
                        )
                    )
        bottling.dib_ranges = new_ranges
        del update_data["dib_ranges"]
    elif "dib_label_start" in update_data or "dib_label_end" in update_data:
        start = bottling_in.dib_label_start if "dib_label_start" in update_data else (bottling.dib_ranges[0].dib_label_start if bottling.dib_ranges else None)
        end = bottling_in.dib_label_end if "dib_label_end" in update_data else (bottling.dib_ranges[0].dib_label_end if bottling.dib_ranges else None)
        
        db.query(HoneyBottlingDIBRange).filter(HoneyBottlingDIBRange.bottling_id == bottling.id).delete()
        if start or end:
            bottling.dib_ranges = [
                HoneyBottlingDIBRange(
                    bottling_id=bottling.id,
                    dib_label_start=start,
                    dib_label_end=end
                )
            ]
        else:
            bottling.dib_ranges = []

    if "dib_label_start" in update_data:
        del update_data["dib_label_start"]
    if "dib_label_end" in update_data:
        del update_data["dib_label_end"]

    for field, value in update_data.items():
        setattr(bottling, field, value)

    db.commit()
    db.refresh(bottling)
    return bottling


@router.delete("/{batch_id}/bottlings/{bottling_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_honey_bottling(
    batch_id: str,
    bottling_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a bottling from a batch."""
    batch = db.query(HoneyBatch).filter(HoneyBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Honig-Charge nicht gefunden")
    check_access(batch.apiary_id, current_user, db)

    bottling = db.query(HoneyBottling).filter(
        HoneyBottling.id == bottling_id,
        HoneyBottling.honey_batch_id == batch_id
    ).first()
    if not bottling:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abfüllung nicht gefunden")

    db.delete(bottling)
    db.commit()
    return


# --- CSV Export ---

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
        "Gesamt-Erntemenge (kg)",
        "Wassergehalt (%)",
        "Erwärmungstemp. (°C)",
        "Mindesthaltbarkeitsdatum (MHD)",
        "MHD Taggenau",
        "Rückstellprobe vorhanden",
        "Rückstellprobe Datum",
        "Rückstellprobe ID",
        "Abfülldatum",
        "Glasgröße (g)",
        "Anzahl Gläser",
        "Abgefüllte Menge (kg)",
        "D.I.B. Gewährverschluss Start",
        "D.I.B. Gewährverschluss Ende",
        "Notizen"
    ])

    for b in batches:
        base_row = [
            b.batch_number or "MHD-Ausnahme",
            b.honey_type,
            b.harvest_date.strftime("%d.%m.%Y") if b.harvest_date else "",
            str(b.quantity_kg).replace('.', ','),
            str(b.water_content_percent).replace('.', ',') if b.water_content_percent is not None else "",
            str(b.heating_temperature_celsius).replace('.', ',') if b.heating_temperature_celsius is not None else "",
            b.best_before_date.strftime("%d.%m.%Y") if b.best_before_date else "",
            "Ja" if b.is_exact_date else "Nein",
            "Ja" if b.reserve_sample_taken else "Nein",
            b.reserve_sample_date.strftime("%d.%m.%Y") if b.reserve_sample_date else "",
            b.reserve_sample_id or ""
        ]

        if b.bottlings and len(b.bottlings) > 0:
            for bottling in b.bottlings:
                dib_start = bottling.dib_label_start or ""
                dib_end = bottling.dib_label_end or ""
                notes_parts = []
                if b.notes:
                    notes_parts.append(f"Charge: {b.notes}")
                if bottling.notes:
                    notes_parts.append(f"Abfüllung: {bottling.notes}")
                if bottling.dib_ranges and len(bottling.dib_ranges) > 1:
                    extra = [f"{r.dib_label_start or '?'} bis {r.dib_label_end or '?'}" for r in bottling.dib_ranges[1:]]
                    notes_parts.append(f"[Weitere Gewährverschlüsse: {', '.join(extra)}]")
                notes_str = " — ".join(notes_parts)

                writer.writerow(base_row + [
                    bottling.bottling_date.strftime("%d.%m.%Y") if bottling.bottling_date else "",
                    str(bottling.jar_size_g) if bottling.jar_size_g else "",
                    str(bottling.quantity_jars) if bottling.quantity_jars is not None else "",
                    str(bottling.quantity_kg).replace('.', ',') if bottling.quantity_kg is not None else "",
                    dib_start,
                    dib_end,
                    notes_str
                ])
        else:
            # Batch without any bottlings yet
            dib_start = b.dib_label_start or ""
            dib_end = b.dib_label_end or ""
            writer.writerow(base_row + [
                "",  # Abfülldatum
                "",  # Glasgröße
                "",  # Anzahl Gläser
                "",  # Abgefüllte Menge
                dib_start,
                dib_end,
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
