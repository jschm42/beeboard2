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
from app.models.administration import LLMConfig
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
        from app.models.apiary import ApiaryMembership
        membership = db.query(ApiaryMembership).filter(
            ApiaryMembership.apiary_id == apiary.id
        ).order_by(ApiaryMembership.role == 'ADMIN').first()
        current_user = membership.user if membership else None

        from app.services.ai_assistant import run_agent_loop
        content = await run_agent_loop(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            db=db,
            apiary_id=apiary.id,
            current_user=current_user,
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

def reschedule_insights_job(cron_expression: str) -> bool:
    """Dynamically reschedules the AI Insights job with the given unix cron expression."""
    # Remove existing job if it exists
    try:
        scheduler.remove_job('ai_insights_job')
    except Exception:
        pass
    
    parts = cron_expression.strip().split()
    if len(parts) == 5:
        minute, hour, day, month, day_of_week = parts
        try:
            scheduler.add_job(
                generate_ai_insights_job,
                'cron',
                id='ai_insights_job',
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            logger.info(f"AI Insights job scheduled with cron: {cron_expression}")
            return True
        except Exception as e:
            logger.warning(f"Failed to schedule cron job with expression '{cron_expression}': {e}")
            
    # Fallback to interval if invalid
    try:
        scheduler.add_job(generate_ai_insights_job, 'interval', hours=12, id='ai_insights_job')
    except Exception:
        pass
    logger.warning(f"Fallback to 12h interval applied due to invalid cron '{cron_expression}'.")
    return False

def start_scheduler():
    # Load cron expression from DB config
    db = SessionLocal()
    try:
        config = get_llm_config(db)
        cron_expression = config.ai_insights_cron or "0 */12 * * *"
    except Exception as e:
        logger.error(f"Error loading cron config on startup: {e}")
        cron_expression = "0 */12 * * *"
    finally:
        db.close()
        
    reschedule_insights_job(cron_expression)
    scheduler.start()
    logger.info(f"APScheduler started (AI insights cron='{cron_expression}').")
