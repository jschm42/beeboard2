from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings, APP_NAME, APP_VERSION, APP_DESCRIPTION
from app.core.database import engine
from app.models import Base
from app.routers import auth, apiaries, locations, hives, logbook, stats, ai, admin, ai_insights, honey, sales, tasks, treatments
from app.routers import bee_agent
from contextlib import asynccontextmanager
from app.services.cron import start_scheduler

# Initialize SQLite tables on startup
from sqlalchemy import text
with engine.connect() as conn:
    try:
        table_exists = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='log_entries'"
        )).fetchone()
        if table_exists:
            result = conn.execute(text("PRAGMA table_info(log_entries)"))
            log_entries_cols = result.fetchall()
            hive_id_info = next((c for c in log_entries_cols if c[1] == "hive_id"), None)
            if hive_id_info and hive_id_info[3] == 1:  # notnull == 1
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                conn.execute(text("ALTER TABLE log_entries RENAME TO log_entries_old"))
                conn.commit()
    except Exception as e:
        print(f"Error checking/renaming log_entries: {e}")

Base.metadata.create_all(bind=engine)

with engine.connect() as conn:
    try:
        old_exists = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='log_entries_old'"
        )).fetchone()
        if old_exists:
            result = conn.execute(text("PRAGMA table_info(log_entries_old)"))
            old_cols = [row[1] for row in result.fetchall()]
            result_new = conn.execute(text("PRAGMA table_info(log_entries)"))
            new_cols = [row[1] for row in result_new.fetchall()]
            common_cols = [c for c in old_cols if c in new_cols]
            cols_str = ", ".join(common_cols)
            conn.execute(text(f"INSERT INTO log_entries ({cols_str}) SELECT {cols_str} FROM log_entries_old"))
            conn.execute(text("DROP TABLE log_entries_old"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()
    except Exception as e:
        print(f"Error migrating/copying log_entries: {e}")

# Database migrations for new columns
from sqlalchemy import text
with engine.connect() as conn:
    try:
        result = conn.execute(text("PRAGMA table_info(llm_configs)"))
        columns = [row[1] for row in result.fetchall()]
        if "ai_insights_cron" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN ai_insights_cron VARCHAR DEFAULT '0 */12 * * *'"))
            conn.commit()
        if "kleinunternehmer_regelung" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN kleinunternehmer_regelung BOOLEAN DEFAULT 0"))
            conn.commit()
        if "currency" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN currency VARCHAR(10) DEFAULT 'EUR'"))
            conn.commit()
        if "tax_rates" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN tax_rates VARCHAR(255) DEFAULT '0.0,7.0,19.0'"))
            conn.commit()
        if "calculate_taxes" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN calculate_taxes BOOLEAN DEFAULT 1"))
            conn.commit()


        result = conn.execute(text("PRAGMA table_info(ai_insights)"))
        ai_insight_columns = [row[1] for row in result.fetchall()]
        if "is_read" not in ai_insight_columns:
            conn.execute(text("ALTER TABLE ai_insights ADD COLUMN is_read BOOLEAN DEFAULT 0 NOT NULL"))
            conn.commit()
        if "read_at" not in ai_insight_columns:
            conn.execute(text("ALTER TABLE ai_insights ADD COLUMN read_at DATETIME"))
            conn.commit()

        result = conn.execute(text("PRAGMA table_info(bee_agent_jobs)"))
        bee_agent_job_columns = [row[1] for row in result.fetchall()]
        if "include_locations" not in bee_agent_job_columns:
            conn.execute(text("ALTER TABLE bee_agent_jobs ADD COLUMN include_locations BOOLEAN DEFAULT 1"))
            conn.commit()
        if "include_hives" not in bee_agent_job_columns:
            conn.execute(text("ALTER TABLE bee_agent_jobs ADD COLUMN include_hives BOOLEAN DEFAULT 1"))
            conn.commit()
        if "include_tasks" not in bee_agent_job_columns:
            conn.execute(text("ALTER TABLE bee_agent_jobs ADD COLUMN include_tasks BOOLEAN DEFAULT 1"))
            conn.commit()
        if "include_calendar" not in bee_agent_job_columns:
            conn.execute(text("ALTER TABLE bee_agent_jobs ADD COLUMN include_calendar BOOLEAN DEFAULT 1"))
            conn.commit()

        result = conn.execute(text("PRAGMA table_info(ai_insight_cron_jobs)"))
        ai_insight_cron_job_columns = [row[1] for row in result.fetchall()]
        if "prompt" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN prompt TEXT DEFAULT 'Erstelle einen praezisen KI-Insight-Bericht fuer Imker.'"))
            conn.commit()
        if "inject_weather" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_weather BOOLEAN DEFAULT 0"))
            conn.commit()
        if "inject_locations" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_locations BOOLEAN DEFAULT 1"))
            conn.commit()
        if "inject_apiary" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_apiary BOOLEAN DEFAULT 1"))
            conn.commit()
        if "inject_hives" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_hives BOOLEAN DEFAULT 1"))
            conn.commit()
        if "inject_log_entries" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN inject_log_entries BOOLEAN DEFAULT 1"))
            conn.commit()
        if "log_scope" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN log_scope VARCHAR(20) DEFAULT 'IMKEREI'"))
            conn.commit()
        if "max_log_entries" not in ai_insight_cron_job_columns:
            conn.execute(text("ALTER TABLE ai_insight_cron_jobs ADD COLUMN max_log_entries INTEGER DEFAULT 20"))
            conn.commit()

        # Log Session Scope Type and association table migrations
        result = conn.execute(text("PRAGMA table_info(log_sessions)"))
        log_session_columns = [row[1] for row in result.fetchall()]
        if "scope_type" not in log_session_columns:
            conn.execute(text("ALTER TABLE log_sessions ADD COLUMN scope_type VARCHAR(20) DEFAULT 'APIARY'"))
            conn.commit()
        
        # Task recurrence and all-day migrations
        result = conn.execute(text("PRAGMA table_info(tasks)"))
        tasks_columns = [row[1] for row in result.fetchall()]
        if "is_all_day" not in tasks_columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN is_all_day BOOLEAN DEFAULT 1"))
            conn.commit()
        if "due_time" not in tasks_columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN due_time VARCHAR(5) DEFAULT NULL"))
            conn.commit()
        if "recurrence_interval_type" not in tasks_columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN recurrence_interval_type VARCHAR(10) DEFAULT NULL"))
            conn.commit()
        if "recurrence_interval_value" not in tasks_columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN recurrence_interval_value INTEGER DEFAULT 1"))
            conn.commit()
        if "recurrence_weekdays" not in tasks_columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN recurrence_weekdays VARCHAR(50) DEFAULT NULL"))
            conn.commit()
        if "recurrence_end_date" not in tasks_columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN recurrence_end_date DATE DEFAULT NULL"))
            conn.commit()

        # Migrate existing log_sessions with hive_id to scope_type='HIVE' and populate log_session_hives
        conn.execute(text("""
            UPDATE log_sessions 
            SET scope_type = 'HIVE' 
            WHERE hive_id IS NOT NULL AND (scope_type IS NULL OR scope_type = 'APIARY')
        """))
        conn.commit()
        
        # Now populate log_session_hives for existing sessions
        result = conn.execute(text("""
            SELECT id, hive_id FROM log_sessions 
            WHERE hive_id IS NOT NULL
        """))
        for row in result.fetchall():
            session_id, hive_id = row[0], row[1]
            exists = conn.execute(text(
                "SELECT 1 FROM log_session_hives WHERE log_session_id = :sid AND hive_id = :hid"
            ), {"sid": session_id, "hid": hive_id}).fetchone()
            if not exists:
                conn.execute(text(
                    "INSERT INTO log_session_hives (log_session_id, hive_id) VALUES (:sid, :hid)"
                ), {"sid": session_id, "hid": hive_id})
        conn.commit()
    except (RuntimeError, ValueError, TypeError) as e:
        print(f"Error running database migration: {e}")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(
    title=f"{APP_NAME} API",
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan
)

# Configure CORS so that our Vue 3 SPA frontend can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Customize in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory to serve uploaded images (hive photos and log images)
# Make sure directory exists
uploads_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(apiaries.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(hives.router, prefix="/api")
app.include_router(logbook.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(ai_insights.router, prefix="/api")
app.include_router(honey.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(bee_agent.router, prefix="/api")
app.include_router(treatments.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}
