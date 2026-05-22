from __future__ import annotations

from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.crypto import decrypt_value, encrypt_value
from app.models.administration import LLMConfig

API_KEY_FIELDS = {
    "GEMINI_API_KEY": "gemini_api_key_encrypted",
    "OPENAI_API_KEY": "openai_api_key_encrypted",
    "OPENROUTER_API_KEY": "openrouter_api_key_encrypted",
    "ANTHROPIC_API_KEY": "anthropic_api_key_encrypted",
    "OPENWEATHERMAP_API_KEY": "openweathermap_api_key_encrypted",
}


def _clean_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def get_llm_config(db: Session) -> LLMConfig:
    from app.services.ai_assistant import DEFAULT_CHATBOT_PROMPT, DEFAULT_DRAFT_PROMPT

    config = db.query(LLMConfig).first()
    if not config:
        config = LLMConfig(
            chatbot_system_prompt=DEFAULT_CHATBOT_PROMPT,
            draft_system_prompt=DEFAULT_DRAFT_PROMPT,
            enable_weather_api=False,
            ai_insights_cron="0 */12 * * *",
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    elif not config.ai_insights_cron:
        config.ai_insights_cron = "0 */12 * * *"
        db.commit()
        db.refresh(config)
    return config


def _resolve_secret(db_encrypted: Optional[str], env_value: Optional[str]) -> Tuple[Optional[str], Optional[str], bool, bool]:
    db_value = _clean_str(decrypt_value(db_encrypted))
    env_clean = _clean_str(env_value)
    if db_value:
        return db_value, "db", True, bool(env_clean)
    if env_clean:
        return env_clean, "env", False, True
    return None, None, False, False


def get_effective_api_key(db: Session, env_name: str) -> Optional[str]:
    config = get_llm_config(db)
    field_name = API_KEY_FIELDS.get(env_name)
    if not field_name:
        return None
    value, _, _, _ = _resolve_secret(getattr(config, field_name), getattr(settings, env_name, None))
    return value


def get_api_key_status(db: Session) -> Dict[str, Dict[str, Optional[str]]]:
    config = get_llm_config(db)
    status: Dict[str, Dict[str, Optional[str]]] = {}
    for env_name, field_name in API_KEY_FIELDS.items():
        _, source, db_configured, env_configured = _resolve_secret(
            getattr(config, field_name), getattr(settings, env_name, None)
        )
        status[env_name] = {
            "db_configured": db_configured,
            "env_configured": env_configured,
            "effective_source": source,
        }
    return status


def set_api_keys(db: Session, values: Dict[str, Optional[str]]) -> LLMConfig:
    config = get_llm_config(db)
    for env_name, field_name in API_KEY_FIELDS.items():
        if env_name not in values:
            continue
        raw_value = values.get(env_name)
        cleaned = _clean_str(raw_value)
        setattr(config, field_name, encrypt_value(cleaned) if cleaned else None)
    db.commit()
    db.refresh(config)
    return config


def set_smtp_settings(db: Session, values: Dict[str, Optional[str]]) -> LLMConfig:
    config = get_llm_config(db)

    if "smtp_host" in values:
        config.smtp_host = _clean_str(values.get("smtp_host"))
    if "smtp_port" in values and values.get("smtp_port") is not None:
        config.smtp_port = int(values["smtp_port"])
    if "smtp_from_email" in values:
        config.smtp_from_email = _clean_str(values.get("smtp_from_email"))
    if "smtp_use_tls" in values and values.get("smtp_use_tls") is not None:
        config.smtp_use_tls = bool(values["smtp_use_tls"])
    if "smtp_use_ssl" in values and values.get("smtp_use_ssl") is not None:
        config.smtp_use_ssl = bool(values["smtp_use_ssl"])

    if "smtp_username" in values:
        username = _clean_str(values.get("smtp_username"))
        config.smtp_username_encrypted = encrypt_value(username) if username else None

    if "smtp_password" in values:
        password = _clean_str(values.get("smtp_password"))
        config.smtp_password_encrypted = encrypt_value(password) if password else None

    db.commit()
    db.refresh(config)
    return config


def get_smtp_settings(db: Session) -> Dict[str, Optional[str]]:
    config = get_llm_config(db)

    db_host = _clean_str(config.smtp_host)
    db_port = config.smtp_port if config.smtp_port else None
    db_from_email = _clean_str(config.smtp_from_email)
    db_username = _clean_str(decrypt_value(config.smtp_username_encrypted))
    db_password = _clean_str(decrypt_value(config.smtp_password_encrypted))

    host = db_host or _clean_str(settings.SMTP_HOST)
    port = db_port or settings.SMTP_PORT
    username = db_username or _clean_str(settings.SMTP_USERNAME)
    password = db_password or _clean_str(settings.SMTP_PASSWORD)
    from_email = db_from_email or _clean_str(settings.SMTP_FROM_EMAIL) or username
    use_tls = config.smtp_use_tls if db_host or db_port or db_from_email or db_username or db_password else settings.SMTP_USE_TLS
    use_ssl = config.smtp_use_ssl if db_host or db_port or db_from_email or db_username or db_password else settings.SMTP_USE_SSL

    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "from_email": from_email,
        "use_tls": use_tls,
        "use_ssl": use_ssl,
        "configured": bool(host and port and from_email),
    }


def get_smtp_status(db: Session) -> Dict[str, Optional[str]]:
    config = get_llm_config(db)
    effective = get_smtp_settings(db)

    db_username = _clean_str(decrypt_value(config.smtp_username_encrypted))
    db_password = _clean_str(decrypt_value(config.smtp_password_encrypted))

    env_host = _clean_str(settings.SMTP_HOST)
    env_username = _clean_str(settings.SMTP_USERNAME)
    env_password = _clean_str(settings.SMTP_PASSWORD)
    env_from_email = _clean_str(settings.SMTP_FROM_EMAIL)

    has_db_values = bool(config.smtp_host or config.smtp_port or config.smtp_from_email or db_username or db_password)
    has_env_values = bool(env_host or env_username or env_password or env_from_email)

    source = "db" if has_db_values else ("env" if has_env_values else None)
    return {
        "host": effective.get("host"),
        "port": effective.get("port"),
        "from_email": effective.get("from_email"),
        "use_tls": effective.get("use_tls"),
        "use_ssl": effective.get("use_ssl"),
        "username_configured": bool(effective.get("username")),
        "password_configured": bool(effective.get("password")),
        "db_configured": has_db_values,
        "env_configured": has_env_values,
        "effective_source": source,
    }
