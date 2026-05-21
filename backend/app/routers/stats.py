from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.hive import Hive
from app.models.logbook import LogEntry, InspectionBox, InspectionDetail
from app.routers.apiaries import check_access
from app.services.calculations import calculate_inspection_totals, detect_season

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/aggregation")
def get_aggregated_stats(
    apiary_id: str = Query(..., description="Active Apiary ID"),
    location_id: Optional[str] = Query(None, description="Filter by Location ID"),
    hive_ids: Optional[List[str]] = Query(None, alias="hive", description="Filter by Hive IDs"),
    year: Optional[int] = Query(None, description="Filter by calendar year"),
    season: Optional[str] = Query(None, description="Filter by season (SPRING, SUMMER, AUTUMN, WINTER)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggregates brood, food, and bee-mass counts across inspection reports.
    Returns labels (dates) and values lists for graphing.
    """
    check_access(apiary_id, current_user, db)

    # Base query for Inspections belonging to the apiary
    query = db.query(LogEntry).filter(
        LogEntry.apiary_id == apiary_id,
        LogEntry.entry_type == "INSPECTION"
    )

    # Apply filters
    if location_id:
        query = query.join(LogEntry.hive).filter(Hive.location_id == location_id)
    if hive_ids:
        query = query.filter(LogEntry.hive_id.in_(hive_ids))
    if year:
        # SQLite compatibility or standard extract
        # date is a Date column
        # In SQLAlchemy: extract('year', LogEntry.date)
        from sqlalchemy import extract
        query = query.filter(extract('year', LogEntry.date) == year)

    # To optimize queries, load inspection details, boxes, hive, and frame type
    query = query.options(
        joinedload(LogEntry.inspection_detail).joinedload(InspectionDetail.boxes),
        joinedload(LogEntry.hive).joinedload(Hive.frame_type)
    ).order_by(LogEntry.date.asc())

    entries = query.all()

    labels = []
    brood_values = []
    food_values = []
    bee_values = []
    drone_values = []
    drone_brood_values = []
    pollen_values = []

    for entry in entries:
        if not entry.inspection_detail or not entry.inspection_detail.boxes:
            continue
            
        # Optional seasonal filter
        ent_season = detect_season(entry.date)
        if season and ent_season != season:
            continue

        totals = calculate_inspection_totals(entry.inspection_detail.boxes, db)
        
        labels.append(entry.date.isoformat())
        brood_values.append(float(totals["brood"]))
        food_values.append(float(totals["food"]))
        bee_values.append(float(totals["bees"]))
        drone_values.append(float(totals.get("drones", 0.0)))
        drone_brood_values.append(float(totals.get("drone_brood", 0.0)))
        pollen_values.append(float(totals.get("pollen", 0.0)))

    return {
        "labels": labels,
        "brood": brood_values,
        "food": food_values,
        "bees": bee_values,
        "drones": drone_values,
        "drone_brood": drone_brood_values,
        "pollen": pollen_values
    }
