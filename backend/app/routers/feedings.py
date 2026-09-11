from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List, Optional, Dict
from collections import defaultdict
import csv
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.hive import Hive
from app.models.feeding import FeedType, Feeding
from app.schemas.feeding import (
    FeedTypeOut, FeedingOut, FeedingCreate, FeedingBatchCreate, FeedingUpdate,
    FeedingStatsSummary, FeedingTypeTotal
)
from app.routers.apiaries import check_access

router = APIRouter(prefix="/feedings", tags=["feedings"])


@router.get("/feed-types", response_model=List[FeedTypeOut])
def list_active_feed_types(db: Session = Depends(get_db)):
    """Lists all active feed types for beekeepers to select in dropdowns."""
    return db.query(FeedType).filter(FeedType.is_active == True).order_by(FeedType.name).all()


@router.get("/stats", response_model=FeedingStatsSummary)
def get_feeding_stats(
    apiary_id: str = Query(..., description="Scope to a specific apiary"),
    hive_id: Optional[str] = Query(None, description="Filter by hive"),
    location_id: Optional[str] = Query(None, description="Filter by location"),
    feed_type_id: Optional[str] = Query(None, description="Filter by feed type"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns aggregated feeding totals grouped by unit and feed type."""
    check_access(apiary_id, current_user, db)

    query = db.query(Feeding).join(Hive).filter(Feeding.apiary_id == apiary_id)

    if hive_id:
        query = query.filter(Feeding.hive_id == hive_id)
    if location_id:
        query = query.filter(Hive.location_id == location_id)
    if feed_type_id:
        query = query.filter(Feeding.feed_type_id == feed_type_id)
    if start_date:
        query = query.filter(Feeding.date >= start_date)
    if end_date:
        query = query.filter(Feeding.date <= end_date)

    feedings = query.options(joinedload(Feeding.feed_type)).all()

    totals_by_unit: Dict[str, float] = defaultdict(float)
    type_stats: Dict[str, Dict] = {}

    for f in feedings:
        unit = f.feed_type.unit if f.feed_type else "kg"
        totals_by_unit[unit] += f.amount

        ft_id = f.feed_type_id
        if ft_id not in type_stats:
            type_stats[ft_id] = {
                "feed_type_id": ft_id,
                "feed_type_name": f.feed_type.name if f.feed_type else "Unbekannt",
                "unit": unit,
                "total_amount": 0.0,
                "count": 0
            }
        type_stats[ft_id]["total_amount"] += f.amount
        type_stats[ft_id]["count"] += 1

    # Round floats nicely
    for u in totals_by_unit:
        totals_by_unit[u] = round(totals_by_unit[u], 2)

    by_feed_type = []
    for item in type_stats.values():
        item["total_amount"] = round(item["total_amount"], 2)
        by_feed_type.append(FeedingTypeTotal(**item))

    by_feed_type.sort(key=lambda x: x.feed_type_name)

    return FeedingStatsSummary(
        total_count=len(feedings),
        totals_by_unit=dict(totals_by_unit),
        by_feed_type=by_feed_type
    )


@router.get("/export/csv")
def export_feedings_csv(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    hive_id: Optional[str] = Query(None, description="Filter by a specific hive"),
    location_id: Optional[str] = Query(None, description="Filter by a specific location"),
    feed_type_id: Optional[str] = Query(None, description="Filter by feed type"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports feedings in the apiary to CSV (filtered)."""
    check_access(apiary_id, current_user, db)

    query = db.query(Feeding).join(Hive).filter(Feeding.apiary_id == apiary_id)

    if hive_id:
        query = query.filter(Feeding.hive_id == hive_id)
    if location_id:
        query = query.filter(Hive.location_id == location_id)
    if feed_type_id:
        query = query.filter(Feeding.feed_type_id == feed_type_id)
    if start_date:
        query = query.filter(Feeding.date >= start_date)
    if end_date:
        query = query.filter(Feeding.date <= end_date)

    feedings = query.options(
        joinedload(Feeding.feed_type),
        joinedload(Feeding.hive).joinedload(Hive.location),
        joinedload(Feeding.created_by)
    ).order_by(Feeding.date.desc(), Feeding.created_at.desc()).all()

    output = io.StringIO()
    output.write('\ufeff')  # UTF-8 BOM
    writer = csv.writer(output, delimiter=';')

    writer.writerow([
        "Datum",
        "Volk",
        "Standort",
        "Futtertyp",
        "Menge",
        "Einheit",
        "Gefüttert von",
        "Notizen"
    ])

    for f in feedings:
        writer.writerow([
            f.date.strftime("%Y-%m-%d") if f.date else "",
            f.hive.name if f.hive else "",
            f.hive.location.name if f.hive and f.hive.location else "",
            f.feed_type.name if f.feed_type else "",
            f.amount,
            f.feed_type.unit if f.feed_type else "",
            f.fed_by or (f"{f.created_by.first_name} {f.created_by.last_name}".strip() if f.created_by else "") or "",
            f.notes or ""
        ])

    output.seek(0)
    response_data = output.getvalue().encode('utf-8-sig')

    return StreamingResponse(
        io.BytesIO(response_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=fuetterungen_{date.today().strftime('%Y-%m-%d')}.csv"}
    )


@router.get("", response_model=List[FeedingOut])
def list_feedings(
    apiary_id: str = Query(..., description="Scope search to a specific apiary"),
    hive_id: Optional[str] = Query(None, description="Filter by a specific hive"),
    location_id: Optional[str] = Query(None, description="Filter by a specific location"),
    feed_type_id: Optional[str] = Query(None, description="Filter by feed type"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all feedings in the apiary with optional filters."""
    check_access(apiary_id, current_user, db)

    query = db.query(Feeding).join(Hive).filter(Feeding.apiary_id == apiary_id)

    if hive_id:
        query = query.filter(Feeding.hive_id == hive_id)
    if location_id:
        query = query.filter(Hive.location_id == location_id)
    if feed_type_id:
        query = query.filter(Feeding.feed_type_id == feed_type_id)
    if start_date:
        query = query.filter(Feeding.date >= start_date)
    if end_date:
        query = query.filter(Feeding.date <= end_date)

    return query.options(
        joinedload(Feeding.feed_type),
        joinedload(Feeding.hive).joinedload(Hive.location)
    ).order_by(Feeding.date.desc(), Feeding.created_at.desc()).all()


@router.post("", response_model=FeedingOut, status_code=status.HTTP_201_CREATED)
def create_feeding(
    payload: FeedingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new feeding entry for a hive."""
    hive = db.query(Hive).filter(Hive.id == payload.hive_id).first()
    if not hive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bienenvolk nicht gefunden."
        )

    check_access(hive.apiary_id, current_user, db)

    feed_type = db.query(FeedType).filter(FeedType.id == payload.feed_type_id).first()
    if not feed_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ausgewählter Futtertyp existiert nicht."
        )

    if payload.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Menge muss größer als 0 sein."
        )

    user_full_name = f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username
    fed_by = payload.fed_by.strip() if payload.fed_by else user_full_name

    new_feeding = Feeding(
        hive_id=payload.hive_id,
        feed_type_id=payload.feed_type_id,
        date=payload.date,
        amount=payload.amount,
        fed_by=fed_by,
        notes=payload.notes,
        apiary_id=hive.apiary_id,
        created_by_id=current_user.id
    )
    db.add(new_feeding)
    db.commit()
    db.refresh(new_feeding)

    return db.query(Feeding).options(
        joinedload(Feeding.feed_type),
        joinedload(Feeding.hive).joinedload(Hive.location)
    ).filter(Feeding.id == new_feeding.id).first()


@router.post("/batch", response_model=List[FeedingOut], status_code=status.HTTP_201_CREATED)
def create_batch_feeding(
    payload: FeedingBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates feeding entries for multiple hives simultaneously with the same feed type and amount."""
    if not payload.hive_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mindestens ein Bienenvolk muss ausgewählt sein."
        )

    feed_type = db.query(FeedType).filter(FeedType.id == payload.feed_type_id).first()
    if not feed_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ausgewählter Futtertyp existiert nicht."
        )

    if payload.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Menge muss größer als 0 sein."
        )

    hives = db.query(Hive).filter(Hive.id.in_(payload.hive_ids)).all()
    if len(hives) != len(payload.hive_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ein oder mehrere Bienenvölker wurden nicht gefunden."
        )

    user_full_name = f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username
    fed_by = payload.fed_by.strip() if payload.fed_by else user_full_name

    new_feedings = []
    for hive in hives:
        check_access(hive.apiary_id, current_user, db)
        f = Feeding(
            hive_id=hive.id,
            feed_type_id=payload.feed_type_id,
            date=payload.date,
            amount=payload.amount,
            fed_by=fed_by,
            notes=payload.notes,
            apiary_id=hive.apiary_id,
            created_by_id=current_user.id
        )
        db.add(f)
        new_feedings.append(f)

    db.commit()

    created_ids = [f.id for f in new_feedings]
    return db.query(Feeding).options(
        joinedload(Feeding.feed_type),
        joinedload(Feeding.hive).joinedload(Hive.location)
    ).filter(Feeding.id.in_(created_ids)).all()


@router.put("/{feeding_id}", response_model=FeedingOut)
def update_feeding(
    feeding_id: str,
    payload: FeedingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates a feeding record."""
    feeding = db.query(Feeding).filter(Feeding.id == feeding_id).first()
    if not feeding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fütterungseintrag nicht gefunden."
        )

    check_access(feeding.apiary_id, current_user, db)

    if payload.hive_id is not None and payload.hive_id != feeding.hive_id:
        new_hive = db.query(Hive).filter(Hive.id == payload.hive_id).first()
        if not new_hive or new_hive.apiary_id != feeding.apiary_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiges Bienenvolk ausgewählt."
            )
        feeding.hive_id = payload.hive_id

    if payload.feed_type_id is not None:
        feed_type = db.query(FeedType).filter(FeedType.id == payload.feed_type_id).first()
        if not feed_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ausgewählter Futtertyp existiert nicht."
            )
        feeding.feed_type_id = payload.feed_type_id

    if payload.amount is not None:
        if payload.amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menge muss größer als 0 sein.")
        feeding.amount = payload.amount

    if payload.date is not None:
        feeding.date = payload.date

    if payload.fed_by is not None:
        feeding.fed_by = payload.fed_by.strip() if payload.fed_by else None

    if payload.notes is not None:
        feeding.notes = payload.notes

    db.commit()
    db.refresh(feeding)

    return db.query(Feeding).options(
        joinedload(Feeding.feed_type),
        joinedload(Feeding.hive).joinedload(Hive.location)
    ).filter(Feeding.id == feeding.id).first()


@router.delete("/{feeding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feeding(
    feeding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a feeding record."""
    feeding = db.query(Feeding).filter(Feeding.id == feeding_id).first()
    if not feeding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fütterungseintrag nicht gefunden."
        )

    check_access(feeding.apiary_id, current_user, db, require_admin=True)

    db.delete(feeding)
    db.commit()
    return
