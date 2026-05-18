import os
import json
import logging
from datetime import date
from typing import Dict, Any, Optional
import litellm
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.administration import LLMConfig

logger = logging.getLogger("beeboard.ai")

DEFAULT_CHATBOT_PROMPT = (
    "Du bist der hochkompetente 'BeeBoard KI-Assistent' für Imker.\n"
    "Deine Aufgabe ist es, dem Imker basierend auf seinen Daten präzise Auskunft "
    "zu geben. Antworte immer freundlich, sachlich und auf Deutsch. Halte dich kurz "
    "und hebe wichtige Warnungen (wie hohe Varroazahlen) hervor.\n\n"
    "Hier ist der aktuelle Zustand der Imkerei (Völker, Standorte, letzte Messungen):\n"
    "{context_str}"
)

DEFAULT_DRAFT_PROMPT = (
    "Du bist ein intelligentere Daten-Extraktor für Imker.\n"
    "Lies die folgende Freitext-Notiz des Imkers durch und wandle sie in ein valides JSON-Objekt um.\n"
    "Das JSON-Objekt MUSS exakt der folgenden Struktur entsprechen. Gib NUR das reine JSON zurück. Keine Markdowns wie ```json.\n\n"
    "STRUKTUR:\n"
    "{\n"
    "  \"hive_name\": \"Name des Volks (z.B. Volk 3) oder null wenn nicht genannt\",\n"
    "  \"entry_type\": \"Einer der Werte: 'INSPECTION', 'VARROA_COUNT', 'VARROA_TREATMENT', 'GENERAL'\",\n"
    "  \"notes\": \"Zusammenfassung der Notiz als Fließtext\",\n"
    "  \"date\": \"Datum im Format YYYY-MM-DD (Standard: '{date_str}')\",\n"
    "  \"inspection_detail\": {\n"
    "    \"frames\": [\n"
    "      {\n"
    "        \"frame_number\": 1, // Nummer der Wabe (1-basiert)\n"
    "        \"side\": 1,         // Waben-Seite (1 oder 2)\n"
    "        \"brood_eighths\": 0, // Brut in Achteln (0-8)\n"
    "        \"food_eighths\": 0,  // Futter in Achteln (0-8)\n"
    "        \"bee_eighths\": 0    // Bienenmasse in Achteln (0-8)\n"
    "      }\n"
    "    ]\n"
    "  }, // Nur vorhanden bei entry_type = 'INSPECTION', sonst null\n"
    "  \"varroa_count_detail\": {\n"
    "    \"raw_count\": 0 // Rohwert Varroamilben (Zahl)\n"
    "  }, // Nur vorhanden bei entry_type = 'VARROA_COUNT', sonst null\n"
    "  \"varroa_treatment_detail\": {\n"
    "    \"product\": \"Name des Präparats\",\n"
    "    \"dosage\": \"Dosis (z.B. 50ml)\"\n"
    "  } // Nur vorhanden bei entry_type = 'VARROA_TREATMENT', sonst null\n"
    "}"
)

def get_llm_config(db: Session) -> LLMConfig:
    """Retrieves or seeds the default LLM prompts and settings from the database."""
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
    return config

async def run_agent_loop(system_prompt: str, user_prompt: str, db: Session, apiary_id: str, effective_model: str, api_key: str) -> str:
    from app.models.location import Location
    from app.models.hive import Hive
    from app.models.logbook import LogEntry
    from app.services.calculations import calculate_inspection_totals
    from app.services.weather import fetch_current_weather
    from datetime import datetime, timedelta
    import json
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_locations",
                "description": "Lädt alle Standorte der aktuellen Imkerei herunter.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_hives",
                "description": "Lädt alle Bienenvölker (Name, Status, Königin, Zargen) der Imkerei herunter.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_recent_log_entries",
                "description": "Lädt die Logbucheinträge und Schätzungen (Inspektion, Varroafall, Behandlung) der letzten N Tage herunter.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "description": "Anzahl der Tage in der Vergangenheit (Standard: 7)"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Lädt das aktuelle Wetter für alle Standorte der Imkerei herunter (via OpenWeatherMap).",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        }
    ]
    
    for _ in range(5):
        try:
            response = await litellm.acompletion(
                model=effective_model,
                messages=messages,
                tools=tools,
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"LiteLLM completion error: {str(e)}")
            return f"Fehler bei der KI-Anfrage: {str(e)}"
            
        response_message = response.choices[0].message
        
        if not response_message.tool_calls:
            return response_message.content or ""
            
        messages.append(response_message.model_dump())
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            arguments = {}
            if tool_call.function.arguments:
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except Exception:
                    pass
            
            result = ""
            try:
                if function_name == "get_locations":
                    locations = db.query(Location).filter(Location.apiary_id == apiary_id).all()
                    res = [f"Standort '{loc.name}' in {loc.address}. Notizen: {loc.notes or 'Keine'}" for loc in locations]
                    result = "\n".join(res) if res else "Keine Standorte gefunden."
                    
                elif function_name == "get_hives":
                    hives = db.query(Hive).filter(Hive.apiary_id == apiary_id).all()
                    res = []
                    for hive in hives:
                        status_str = "Aktiv" if hive.is_active else "Inaktiv"
                        queen_str = f"Königin aus {hive.queen_year}" if hive.queen_year else "Königin-Jahr unbekannt"
                        boxes_str = f"{len(hive.boxes)} Zargen"
                        res.append(f"- Volk '{hive.name}' ({status_str}): Standort='{hive.location.name if hive.location else 'Unbekannt'}', {queen_str}, Struktur={boxes_str}.")
                    result = "\n".join(res) if res else "Keine Bienenvölker gefunden."
                    
                elif function_name == "get_recent_log_entries":
                    days = arguments.get("days", 7)
                    threshold = datetime.utcnow().date() - timedelta(days=days)
                    recent_entries = db.query(LogEntry).filter(
                        LogEntry.apiary_id == apiary_id,
                        LogEntry.date >= threshold
                    ).order_by(LogEntry.date.desc()).all()
                    res = []
                    for entry in recent_entries:
                        detail_desc = ""
                        if entry.entry_type == "INSPECTION" and entry.inspection_detail:
                            totals = calculate_inspection_totals(entry.inspection_detail.frames, db)
                            detail_desc = f"Brut={totals.get('brood',0)} Waben, Futter={totals.get('food',0)} Waben, Bienen={totals.get('bees',0)} Waben"
                        elif entry.entry_type == "VARROA_COUNT" and entry.varroa_count_detail:
                            detail_desc = f"Milbenfall={entry.varroa_count_detail.raw_count}, Geschätzt={entry.varroa_count_detail.estimated_total}"
                        elif entry.entry_type == "VARROA_TREATMENT" and entry.varroa_treatment_detail:
                            detail_desc = f"Behandlung {entry.varroa_treatment_detail.product} ({entry.varroa_treatment_detail.dosage})"
                        res.append(f"- [{entry.date}] Volk: '{entry.hive.name if entry.hive else 'Unbekannt'}' | Typ: {entry.entry_type} | Details: {detail_desc}")
                    result = "\n".join(res) if res else f"Keine Logbucheinträge in den letzten {days} Tagen gefunden."
                    
                elif function_name == "get_current_weather":
                    locations = db.query(Location).filter(Location.apiary_id == apiary_id).all()
                    res = []
                    for loc in locations:
                        if loc.latitude and loc.longitude:
                            w = await fetch_current_weather(loc.latitude, loc.longitude)
                            if w:
                                temp = w.get("temp", 0.0)
                                humidity = w.get("humidity", 0)
                                wind = w.get("wind_speed", 0.0)
                                weather_desc = w.get("weather", [{}])[0].get("description", "Unbekannt")
                                res.append(f"Standort '{loc.name}': {temp}°C, {weather_desc}, Feuchte: {humidity}%, Wind: {wind} m/s")
                    result = "\n".join(res) if res else "Konnte keine Wetterdaten abrufen (oder keine Geodaten)."
                else:
                    result = f"Unbekannte Funktion: {function_name}"
            except Exception as e:
                result = f"Fehler bei Funktionsausführung: {str(e)}"
                
            messages.append({
                "role": "tool",
                "name": function_name,
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
            
    return "Der Assistent konnte die Anfrage nicht innerhalb der maximalen Anzahl von Schritten beantworten."


def get_effective_model_and_key(model: str) -> tuple[str, Optional[str]]:
    """
    Resolves the effective model name and API key to use.
    If the direct provider API key is missing but OPENROUTER_API_KEY is configured,
    automatically routes the request via OpenRouter by prefixing 'openrouter/' to the model.
    """
    # 1. If the model explicitly requests openrouter
    if "openrouter" in model:
        return model, (settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY"))

    # 2. Check direct provider keys
    if "claude" in model or "anthropic" in model:
        direct_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        if direct_key:
            return model, direct_key
    elif "gemini" in model:
        direct_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if direct_key:
            return model, direct_key
    elif "gpt" in model or "openai" in model:
        direct_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if direct_key:
            return model, direct_key
    else:
        direct_key = None

    # 3. Fallback to OpenRouter if configured
    openrouter_key = settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        effective_model = model
        if not model.startswith("openrouter/"):
            effective_model = f"openrouter/{model}"
        return effective_model, openrouter_key

    # 4. If no openrouter key, return direct key even if None (to trigger fallback warning)
    if "claude" in model or "anthropic" in model:
        return model, (settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY"))
    if "gemini" in model:
        return model, (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
    if "gpt" in model or "openai" in model:
        return model, (settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))

    return model, None

def get_api_key_for_model(model: str) -> Optional[str]:
    """Helper to resolve the correct API key from settings or environment."""
    _, key = get_effective_model_and_key(model)
    return key

async def chatbot_completion(query: str, apiary_id: str, db: Session) -> str:
    """
    Sends the user query along with tool access to the LLM
    to generate helpful, context-aware advice for the beekeeper.
    """
    effective_model, api_key = get_effective_model_and_key(settings.LITELLM_MODEL)
    
    # If no API key is provided, gracefully inform the user or fall back
    if not api_key and not effective_model.startswith("ollama"):
        return (
            "Der KI-Assistent ist bereit, aber es wurde kein API-Schlüssel für "
            f"'{settings.LITELLM_MODEL}' konfiguriert. Bitte hinterlege einen "
            "passenden API-Schlüssel (z.B. GEMINI_API_KEY, OPENROUTER_API_KEY, ANTHROPIC_API_KEY) in den Umgebungsvariablen."
        )

    config = get_llm_config(db)
    system_prompt = config.chatbot_system_prompt.replace("{context_str}", "Du hast Zugriff auf Tools, um dir alle benötigten Daten (Wetter, Logbuch, Völker, Standorte) selbst abzurufen. Nutze sie!")

    try:
        return await run_agent_loop(system_prompt, query, db, apiary_id, effective_model, api_key)
    except Exception as e:
        logger.error(f"LiteLLM error: {str(e)}")
        return f"Entschuldigung, es gab einen Fehler bei der Bearbeitung deiner Anfrage: {str(e)}"

def draft_entry_from_text(freetext: str, date_str: Optional[str] = None, db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Uses the LLM to parse unstructured audio transcripts or notes
    and converts them into a structured JSON draft for a log entry.
    """
    if not date_str:
        date_str = date.today().isoformat()

    effective_model, api_key = get_effective_model_and_key(settings.LITELLM_MODEL)
    
    # Graceful fallback if no API key is set, so the app remains usable
    if not api_key and not effective_model.startswith("ollama"):
        logger.warning("No API key configured for auto-drafting. Using rule-based fallback.")
        return get_fallback_draft(freetext, date_str)

    # Load system prompt from DB if db session is provided, otherwise fallback to default
    if db:
        config = get_llm_config(db)
        prompt_tmpl = config.draft_system_prompt
    else:
        prompt_tmpl = DEFAULT_DRAFT_PROMPT

    system_prompt = prompt_tmpl.replace("{date_str}", date_str)

    try:
        response = litellm.completion(
            model=effective_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": freetext}
            ],
            api_key=api_key,
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        # Clean potential markdown wrappers
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        return json.loads(content)
    except Exception as e:
        logger.error(f"LiteLLM auto-draft error: {str(e)}")
        return get_fallback_draft(freetext, date_str, error=str(e))

def get_fallback_draft(freetext: str, date_str: str, error: Optional[str] = None) -> Dict[str, Any]:
    """Generates a structured dictionary from text if LLM extraction fails or is unconfigured."""
    text_lower = freetext.lower()
    
    # Basic rule-based classification for seamless UX without AI keys
    entry_type = "GENERAL"
    if "milben" in text_lower or "varroa" in text_lower or "zählung" in text_lower or "gezählt" in text_lower:
        if "behandlung" in text_lower or "behandelt" in text_lower or "präparat" in text_lower:
            entry_type = "VARROA_TREATMENT"
        else:
            entry_type = "VARROA_COUNT"
    elif "kontrolliert" in text_lower or "inspektion" in text_lower or "brut" in text_lower or "wabe" in text_lower:
        entry_type = "INSPECTION"

    # Extract single digits for varroa raw count as a guess
    raw_count = 0
    if entry_type == "VARROA_COUNT":
        words = text_lower.split()
        for w in words:
            if w.isdigit():
                raw_count = int(w)
                break

    # Search for hive name
    hive_name = None
    for i in range(1, 20):
        if f"volk {i}" in text_lower or f"volk{i}" in text_lower:
            hive_name = f"Volk {i}"
            break

    notes = freetext
    if error:
        notes += f"\n\n(Hinweis: KI-Extraktion fehlgeschlagen - {error})"

    draft = {
        "hive_name": hive_name,
        "entry_type": entry_type,
        "notes": notes,
        "date": date_str,
        "inspection_detail": None,
        "varroa_count_detail": None,
        "varroa_treatment_detail": None
    }

    if entry_type == "VARROA_COUNT":
        draft["varroa_count_detail"] = {"raw_count": raw_count}
    elif entry_type == "VARROA_TREATMENT":
        draft["varroa_treatment_detail"] = {"product": "Unbekannt", "dosage": ""}
    elif entry_type == "INSPECTION":
        draft["inspection_detail"] = {"frames": []}

    return draft
