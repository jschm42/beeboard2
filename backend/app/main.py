from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.routers import auth, apiaries, locations, hives, logbook, stats, ai, admin, ai_insights
from contextlib import asynccontextmanager
from app.services.cron import start_scheduler

# Initialize SQLite tables on startup
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Backend for BeeBoard - Reactive Beekeeping Log",
    version="2.0.0",
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

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}
