import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.apiary import Apiary
from app.models.location import Location
from app.models.hive import Hive
from app.models.ai_insight import AIInsight
from app.services.weather import fetch_current_weather
from app.services.ai_assistant import get_effective_model_and_key, get_llm_config
import litellm
from app.core.config import settings

logger = logging.getLogger("beeboard.cron")

scheduler = AsyncIOScheduler()

async def generate_ai_insights_job():
    logger.info("Starting scheduled AI Insights job...")
    db = SessionLocal()
    try:
        apiaries = db.query(Apiary).all()
        for apiary in apiaries:
            try:
                await generate_insight_for_apiary(db, apiary)
            except Exception as e:
                logger.error(f"Error generating insight for apiary {apiary.id}: {e}")
    finally:
        db.close()
    logger.info("Finished AI Insights job.")

async def generate_insight_for_apiary(db: Session, apiary: Apiary):
    # Gather Context
    locations = db.query(Location).filter(Location.apiary_id == apiary.id).all()
    hives = db.query(Hive).filter(Hive.apiary_id == apiary.id).all()
    
    context_lines = []
    context_lines.append(f"Imkerei: {apiary.name}")
    
    # Weather
    weather_info = []
    for loc in locations:
        if loc.latitude and loc.longitude:
            w = await fetch_current_weather(loc.latitude, loc.longitude)
            if w:
                temp = w.get("temp", 0.0)
                humidity = w.get("humidity", 0)
                wind = w.get("wind_speed", 0.0)
                weather_desc = w.get("weather", [{}])[0].get("description", "Unbekannt")
                weather_info.append(f"Standort '{loc.name}': {temp}°C, {weather_desc}, Feuchtigkeit: {humidity}%, Wind: {wind} m/s")
    
    if weather_info:
        context_lines.append("\nAKTUELLES WETTER:")
        context_lines.extend(weather_info)
        
    # Hives summary
    active_hives = [h for h in hives if h.is_active]
    context_lines.append(f"\nBIENENVÖLKER: {len(active_hives)} aktive Völker von insgesamt {len(hives)}.")
    
    context_str = "\n".join(context_lines)
    
    # Prompt LLM
    effective_model, api_key = get_effective_model_and_key(settings.LITELLM_MODEL)
    if not api_key and not effective_model.startswith("ollama"):
        logger.warning("No LLM API key configured. Skipping AI Insight generation.")
        return
        
    system_prompt = (
        "Du bist ein intelligenter Imker-Assistent. Analysiere die folgenden Daten "
        "der Imkerei und schreibe einen kurzen, motivierenden Blog-Eintrag (in Markdown) "
        "mit Hinweisen, was bei dem aktuellen Wetter und der Jahreszeit zu beachten ist. "
        "Verwende Emojis und halte es informativ aber kurz."
    )
    
    try:
        # LLM Call (sync wrapped in asyncio if needed, litellm.acompletion is better)
        response = await litellm.acompletion(
            model=effective_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Hier sind die Daten:\n{context_str}"}
            ],
            api_key=api_key
        )
        content = response.choices[0].message.content.strip()
        
        # Save to DB
        insight = AIInsight(
            apiary_id=apiary.id,
            title="Aktuelle Imkerei-Analyse",
            content=content
        )
        db.add(insight)
        db.commit()
        logger.info(f"Saved new AI Insight for apiary {apiary.id}")
        
    except Exception as e:
        logger.error(f"LiteLLM error in cron job: {e}")

def start_scheduler():
    # Run every 12 hours
    scheduler.add_job(generate_ai_insights_job, 'interval', hours=12)
    scheduler.start()
    logger.info("APScheduler started.")
