from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ai_insight import AIInsight
from app.routers.apiaries import check_access
from app.services.cron import generate_insight_for_apiary

router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])

class AIInsightSchema(BaseModel):
    id: str
    apiary_id: str
    title: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[AIInsightSchema])
def list_insights(
    apiary_id: str = Query(...),
    start_date: Optional[datetime] = Query(None, description="Filter: nur Insights ab diesem Datum"),
    end_date: Optional[datetime] = Query(None, description="Filter: nur Insights bis zu diesem Datum"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_access(apiary_id, current_user, db)
    query = db.query(AIInsight).filter(AIInsight.apiary_id == apiary_id)

    if start_date:
        query = query.filter(AIInsight.created_at >= start_date)
    if end_date:
        query = query.filter(AIInsight.created_at <= end_date)

    insights = query.order_by(AIInsight.created_at.desc()).all()
    return insights


@router.delete("/{insight_id}", status_code=204)
def delete_insight(
    insight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    insight = db.query(AIInsight).filter(AIInsight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight nicht gefunden")

    check_access(insight.apiary_id, current_user, db)
    db.delete(insight)
    db.commit()
    return None

@router.get("/latest", response_model=Optional[AIInsightSchema])
def get_latest_insight(
    apiary_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_access(apiary_id, current_user, db)
    insight = db.query(AIInsight).filter(AIInsight.apiary_id == apiary_id).order_by(AIInsight.created_at.desc()).first()
    return insight

@router.post("/trigger", response_model=dict)
async def trigger_insight(
    apiary_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger the generation of a new insight."""
    from app.models.apiary import Apiary
    check_access(apiary_id, current_user, db)
    apiary = db.query(Apiary).filter(Apiary.id == apiary_id).first()
    if not apiary:
        raise HTTPException(status_code=404, detail="Apiary not found")
    
    await generate_insight_for_apiary(db, apiary)
    return {"status": "success", "message": "Insight generated"}
