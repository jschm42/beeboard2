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
    # Prompt LLM
    effective_model, api_key = get_effective_model_and_key(settings.LITELLM_MODEL)
    if not api_key and not effective_model.startswith("ollama"):
        logger.warning("No LLM API key configured. Skipping AI Insight generation.")
        return
        
    system_prompt = (
        "Du bist ein intelligenter Imker-Assistent. Analysiere die Daten der Imkerei "
        "und schreibe einen kurzen, motivierenden Blog-Eintrag (in Markdown) "
        "mit einem Imker-Wetterbericht und Hinweisen, was bei dem aktuellen Wetter und der Jahreszeit "
        "sowie den aktuellen Diagnosen zu beachten ist. "
        "Nutze deine Tools, um dir alle benötigten Daten (Wetter, Standorte, Völker, Logbuch) selbst zu beschaffen! "
        "Verwende Emojis und halte es informativ aber kurz."
    )
    user_prompt = "Bitte lade dir alle aktuellen Daten der Imkerei herunter und erstelle den Bericht."
    
    try:
        from app.services.ai_assistant import run_agent_loop
        content = await run_agent_loop(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            db=db,
            apiary_id=apiary.id,
            effective_model=effective_model,
            api_key=api_key
        )
        
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
