from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings, APP_NAME, APP_VERSION, APP_DESCRIPTION
from app.core.database import engine
from app.models import Base
from app.routers import auth, apiaries, locations, hives, logbook, stats, ai, admin, ai_insights, honey, sales, tasks
from contextlib import asynccontextmanager
from app.services.cron import start_scheduler
from app.core.security import ensure_encrypted_password_hash

# Initialize SQLite tables on startup
Base.metadata.create_all(bind=engine)

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
        if "gemini_api_key_encrypted" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN gemini_api_key_encrypted TEXT"))
            conn.commit()
        if "openai_api_key_encrypted" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN openai_api_key_encrypted TEXT"))
            conn.commit()
        if "openrouter_api_key_encrypted" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN openrouter_api_key_encrypted TEXT"))
            conn.commit()
        if "anthropic_api_key_encrypted" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN anthropic_api_key_encrypted TEXT"))
            conn.commit()
        if "openweathermap_api_key_encrypted" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN openweathermap_api_key_encrypted TEXT"))
            conn.commit()
        if "smtp_host" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN smtp_host VARCHAR(255)"))
            conn.commit()
        if "smtp_port" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN smtp_port INTEGER DEFAULT 587"))
            conn.commit()
        if "smtp_username_encrypted" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN smtp_username_encrypted TEXT"))
            conn.commit()
        if "smtp_password_encrypted" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN smtp_password_encrypted TEXT"))
            conn.commit()
        if "smtp_from_email" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN smtp_from_email VARCHAR(255)"))
            conn.commit()
        if "smtp_use_tls" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN smtp_use_tls BOOLEAN DEFAULT 1"))
            conn.commit()
        if "smtp_use_ssl" not in columns:
            conn.execute(text("ALTER TABLE llm_configs ADD COLUMN smtp_use_ssl BOOLEAN DEFAULT 0"))
            conn.commit()

        result = conn.execute(text("PRAGMA table_info(ai_insights)"))
        ai_insight_columns = [row[1] for row in result.fetchall()]
        if "is_read" not in ai_insight_columns:
            conn.execute(text("ALTER TABLE ai_insights ADD COLUMN is_read BOOLEAN DEFAULT 0 NOT NULL"))
            conn.commit()
        if "read_at" not in ai_insight_columns:
            conn.execute(text("ALTER TABLE ai_insights ADD COLUMN read_at DATETIME"))
            conn.commit()

        users = conn.execute(text("SELECT id, hashed_password FROM users WHERE hashed_password IS NOT NULL")).fetchall()
        for user_id, current_hash in users:
            new_hash = ensure_encrypted_password_hash(current_hash)
            if new_hash != current_hash:
                conn.execute(
                    text("UPDATE users SET hashed_password = :hashed_password WHERE id = :user_id"),
                    {"hashed_password": new_hash, "user_id": user_id},
                )
        conn.commit()
    except Exception as e:
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

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}
