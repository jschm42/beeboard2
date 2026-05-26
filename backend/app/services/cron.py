import asyncio
import json
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

# Semaphore ensures bee-agent jobs run sequentially to prevent OOM with local LLMs
_bee_agent_semaphore = asyncio.Semaphore(1)

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
        "Verwende Emojis und halte es informativ aber kurz. "
        "WICHTIG: Gib NUR den reinen Markdown-Text zurück. Verwende KEINE Markdown-Code-Blöcke wie ```markdown, um die Antwort zu umschließen!"
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

    # Schedule all active Bee-Agent jobs
    _schedule_all_bee_agent_jobs()

    scheduler.start()
    logger.info(f"APScheduler started (AI insights cron='{cron_expression}').")


# ---------------------------------------------------------------------------
# Bee-Agent job scheduling
# ---------------------------------------------------------------------------

def _bee_agent_job_id(job_id: str) -> str:
    return f"bee_agent_job_{job_id}"


def schedule_bee_agent_job(job) -> None:
    """Adds or replaces an APScheduler entry for the given BeeAgentJob."""
    sched_id = _bee_agent_job_id(job.id)
    try:
        scheduler.remove_job(sched_id)
    except Exception:
        pass

    parts = job.cron_expression.strip().split()
    if len(parts) != 5:
        logger.warning(
            f"Invalid cron expression for bee-agent job {job.id}: '{job.cron_expression}'. Skipping."
        )
        return

    minute, hour, day, month, day_of_week = parts
    try:
        scheduler.add_job(
            run_bee_agent_job_queued,
            "cron",
            id=sched_id,
            args=[job.id],
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
        )
        logger.info(f"Bee-Agent job '{job.name}' ({job.id}) scheduled: '{job.cron_expression}'")
    except Exception as e:
        logger.error(f"Failed to schedule bee-agent job {job.id}: {e}")


def remove_bee_agent_job_schedule(job_id: str) -> None:
    """Removes the APScheduler entry for the given job ID."""
    try:
        scheduler.remove_job(_bee_agent_job_id(job_id))
        logger.info(f"Removed schedule for bee-agent job {job_id}")
    except Exception:
        pass


def _schedule_all_bee_agent_jobs() -> None:
    """On startup, load all active BeeAgentJobs from the DB and schedule them."""
    db = SessionLocal()
    try:
        from app.models.bee_agent import BeeAgentJob
        jobs = db.query(BeeAgentJob).filter(BeeAgentJob.is_active.is_(True)).all()
        for job in jobs:
            schedule_bee_agent_job(job)
        logger.info(f"Scheduled {len(jobs)} active Bee-Agent job(s) on startup.")
    except Exception as e:
        logger.error(f"Error scheduling bee-agent jobs on startup: {e}")
    finally:
        db.close()


async def run_bee_agent_job_queued(job_id: str) -> None:
    """Queued entry point — ensures only one bee-agent job runs at a time."""
    async with _bee_agent_semaphore:
        await _run_bee_agent_job(job_id)


async def _run_bee_agent_job(job_id: str) -> None:
    """Executes a single BeeAgentJob run."""
    db = SessionLocal()
    try:
        from app.models.bee_agent import BeeAgentJob, BeeAgentProposal
        from app.services.bee_agent_prompt_builder import BeeAgentPromptBuilder
        from app.services.ai_assistant import run_agent_loop
        from app.models.task import Task
        import re
        from datetime import date as date_type

        job = db.query(BeeAgentJob).filter(BeeAgentJob.id == job_id).first()
        if not job:
            logger.warning(f"Bee-Agent job {job_id} not found.")
            return

        logger.info(f"Running Bee-Agent job '{job.name}' ({job.id}), mode={job.execution_mode}")

        effective_model, api_key = get_effective_model_and_key(settings.LITELLM_MODEL)
        if not api_key and not effective_model.startswith("ollama"):
            logger.warning("No LLM API key configured. Skipping Bee-Agent job.")
            return

        builder = BeeAgentPromptBuilder(job, db)
        system_prompt = builder.build_system_prompt()
        user_prompt = "Analysiere die Daten und erstelle eine Liste mit konkreten Aufgaben als JSON."

        # Determine representative user for weather tool access
        current_user = None
        try:
            from app.models.apiary import ApiaryMembership
            membership = db.query(ApiaryMembership).filter(
                ApiaryMembership.apiary_id == job.apiary_id
            ).first()
            current_user = membership.user if membership else None
        except Exception:
            pass

        raw_output = await run_agent_loop(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            db=db,
            apiary_id=job.apiary_id,
            current_user=current_user,
            effective_model=effective_model,
            api_key=api_key,
        )

        # Parse JSON proposals from agent output
        proposals_data = _parse_proposals(raw_output)
        if not proposals_data:
            logger.info(f"Bee-Agent job '{job.name}' produced no proposals.")
            return

        logger.info(f"Bee-Agent job '{job.name}' produced {len(proposals_data)} proposal(s).")

        for p in proposals_data:
            title = str(p.get("title", "")).strip()
            if not title:
                continue

            due_date_raw = p.get("due_date")
            due_date = None
            if due_date_raw:
                try:
                    due_date = date_type.fromisoformat(str(due_date_raw))
                except (ValueError, TypeError):
                    due_date = None

            if job.execution_mode == "AUTO_CREATE":
                new_task = Task(
                    title=title,
                    description=p.get("description"),
                    due_date=due_date,
                    priority=p.get("priority", "MEDIUM"),
                    location_id=p.get("location_id") or None,
                    hive_id=p.get("hive_id") or None,
                    is_recurring=False,
                    apiary_id=job.apiary_id,
                    created_by_id=job.created_by_id,
                    is_completed=False,
                )
                db.add(new_task)
            else:  # SUGGESTION
                proposal = BeeAgentProposal(
                    job_id=job.id,
                    apiary_id=job.apiary_id,
                    title=title,
                    description=p.get("description"),
                    due_date=due_date,
                    priority=p.get("priority", "MEDIUM"),
                    location_id=p.get("location_id") or None,
                    hive_id=p.get("hive_id") or None,
                    is_accepted=False,
                )
                db.add(proposal)

        db.commit()
        logger.info(f"Bee-Agent job '{job.name}' completed successfully.")

    except Exception as e:
        logger.error(f"Error running Bee-Agent job {job_id}: {e}")
    finally:
        db.close()


def _parse_proposals(raw_output: str) -> list:
    """Extracts the proposals list from the LLM's JSON output."""
    import re

    if not raw_output:
        return []

    # Strip markdown code fences if present
    text = re.sub(r"^```[a-z]*\n?", "", raw_output.strip(), flags=re.MULTILINE)
    text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)
    text = text.strip()

    try:
        data = json.loads(text)
        proposals = data.get("proposals", [])
        return proposals if isinstance(proposals, list) else []
    except (ValueError, TypeError):
        logger.warning("Bee-Agent: Could not parse JSON proposals from LLM output.")
        return []
