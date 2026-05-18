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
    get_llm_config,
    fetch_weather,
    translate_wmo_code
)
from app.services.calculations import calculate_inspection_totals

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=AIChatResponse)
def ai_chat(
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

    # 1. Fetch locations
    locations = db.query(Location).filter(Location.apiary_id == apiary_id).all()

    # 2. Fetch hives
    hives = db.query(Hive).filter(Hive.apiary_id == apiary_id).all()

    # 3. Fetch recent log entries
    recent_entries = db.query(LogEntry).filter(
        LogEntry.apiary_id == apiary_id
    ).order_by(LogEntry.date.desc()).limit(15).all()

    # Compile context string for the AI model
    context_lines = []
    context_lines.append(f"Imker-Konto: {current_user.username} (E-Mail: {current_user.email})")
    
    context_lines.append("\nSTANDORTE:")
    for loc in locations:
        context_lines.append(f"- '{loc.name}' in {loc.address}. Notizen: {loc.notes or 'Keine'}")

    context_lines.append("\nBIENENVÖLKER:")
    for hive in hives:
        status_str = "Aktiv" if hive.is_active else "Inaktiv"
        queen_str = f"Königin aus {hive.queen_year}" if hive.queen_year else "Königin-Jahr unbekannt"
        boxes_str = f"{len(hive.boxes)} Zargen"
        context_lines.append(
            f"- Volk '{hive.name}' ({status_str}): Standort='{hive.location.name}', "
            f"Rahmenmaß='{hive.frame_type.name}', {queen_str}, Struktur={boxes_str}. "
            f"Notizen: {hive.notes or 'Keine'}"
        )

    context_lines.append("\nKÜRZLICHE INSPEKTIONEN & DIAGNOSEN:")
    for entry in recent_entries:
        detail_desc = ""
        if entry.entry_type == "INSPECTION" and entry.inspection_detail:
            totals = calculate_inspection_totals(entry.inspection_detail.frames, db)
            detail_desc = f"Brut={totals['brood']} Waben, Futter={totals['food']} Waben, Bienen={totals['bees']} Waben"
        elif entry.entry_type == "VARROA_COUNT" and entry.varroa_count_detail:
            detail_desc = (
                f"Milbenfall={entry.varroa_count_detail.raw_count} (Rohwert), "
                f"Saison={entry.varroa_count_detail.season}, "
                f"Geschätzter Gesamtbefall={entry.varroa_count_detail.estimated_total} Milben"
            )
        elif entry.entry_type == "VARROA_TREATMENT" and entry.varroa_treatment_detail:
            detail_desc = (
                f"Behandlung mit {entry.varroa_treatment_detail.product}, "
                f"Dosierung={entry.varroa_treatment_detail.dosage}. "
                f"Notiz: {entry.varroa_treatment_detail.treatment_notes or 'Keine'}"
            )
            
        context_lines.append(
            f"- [{entry.date}] Volk: '{entry.hive.name}' | Typ: {entry.entry_type} | "
            f"Notiz: {entry.notes or ''} | Messung: {detail_desc}"
        )

    # Fetch and integrate current weather if enabled
    config = get_llm_config(db)
    if config.enable_weather_api:
        weather_info = []
        for loc in locations:
            if loc.latitude is not None and loc.longitude is not None:
                w = fetch_weather(loc.latitude, loc.longitude)
                if w:
                    weather_desc = translate_wmo_code(w.get("weather_code", 0))
                    temp = w.get("temperature_2m", 0.0)
                    wind = w.get("wind_speed_10m", 0.0)
                    humidity = w.get("relative_humidity_2m", 0)
                    weather_info.append(
                        f"Standort '{loc.name}': {temp}°C, {weather_desc}, "
                        f"Feuchtigkeit: {humidity}%, Windgeschwindigkeit: {wind} km/h"
                    )
        if weather_info:
            context_lines.append("\nAKTUELLES WETTER AN DEN STANDORTEN:")
            context_lines.extend(f"- {info}" for info in weather_info)

    context_str = "\n".join(context_lines)
    
    # Query LiteLLM with database session support for dynamic prompt templates
    response_content = chatbot_completion(query_in.query, context_str, db=db)
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
