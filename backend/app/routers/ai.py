from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.hive import Hive
from app.models.location import Location
from app.models.logbook import LogEntry
from app.schemas.ai import AIChatQuery, AIChatResponse, AIDraftQuery, AIDraftResponse
from app.routers.apiaries import check_access
from app.services.ai_assistant import (
    chatbot_completion, 
    draft_entry_from_text,
    draft_honey_batch_from_text,
    get_llm_config
)
from app.services.calculations import calculate_inspection_totals

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    query_in: AIChatQuery,
    apiary_id: str = Query(..., description="Active Apiary ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Interacts with the AI chatbot to get contextual answers about the
    beekeeper's stand, hives, history, and seasonal diagnostics.
    """
    check_access(apiary_id, current_user, db)

    # Query LiteLLM with database session support for dynamic prompt templates
    response_content = await chatbot_completion(query_in.query, apiary_id, db=db)
    return {"response": response_content}

@router.post("/draft", response_model=AIDraftResponse)
def ai_draft_entry(
    query_in: AIDraftQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parses natural language notes into structured draft data
    so that the beekeeper can quickly auto-fill inspections or counts.
    """
    draft = draft_entry_from_text(query_in.text, db=db)
    return {"draft": draft}

@router.post("/draft-honey", response_model=AIDraftResponse)
def ai_draft_honey_batch(
    query_in: AIDraftQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parses natural language notes into structured honey batch draft data
    so that the beekeeper can quickly auto-fill honey harvests/bottlings.
    """
    draft = draft_honey_batch_from_text(query_in.text, db=db)
    return {"draft": draft}
