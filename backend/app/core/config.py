import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Read shared app version from repo root.
_VERSION_FALLBACK = "2.1.0"
_VERSION_FILE = Path(__file__).resolve().parents[3] / "VERSION"


def _load_app_version() -> str:
    try:
        version = _VERSION_FILE.read_text(encoding="utf-8").strip()
        return version or _VERSION_FALLBACK
    except OSError:
        return _VERSION_FALLBACK


# ---------------------------------------------------------------------------
# BeeBoard — zentrale App-Konstanten (nicht per .env konfigurierbar)
# ---------------------------------------------------------------------------
APP_NAME: str = "BeeBoard"
APP_VERSION: str = _load_app_version()
APP_DESCRIPTION: str = "Reaktives Imkerei-Managementsystem"


class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkeychangeinproduction1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./data/beeboard.db"

    # LiteLLM Configuration
    LITELLM_MODEL: str = "gemini/gemini-2.5-flash"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENWEATHERMAP_API_KEY: Optional[str] = None
    
    # Uploads Configuration
    UPLOAD_DIR: str = "./data/uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
os.makedirs("./data", exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "hives/photos"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "logbook/images"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "logbook/thumbnails"), exist_ok=True)
