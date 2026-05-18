import os
import json
import logging
from datetime import date
from typing import Dict, Any, Optional
import litellm

from app.core.config import settings

logger = logging.getLogger("beeboard.ai")

def get_api_key_for_model(model: str) -> Optional[str]:
    """Helper to resolve the correct API key from settings or environment."""
    if "gemini" in model:
        return settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if "gpt" in model or "openai" in model:
        return settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    return None

def chatbot_completion(query: str, context_str: str) -> str:
    """
    Sends the user query along with apiary status context to the LLM
    to generate helpful, context-aware advice for the beekeeper.
    """
    api_key = get_api_key_for_model(settings.LITELLM_MODEL)
    
    # If no API key is provided, gracefully inform the user or fall back
    if not api_key and not settings.LITELLM_MODEL.startswith("ollama"):
        return (
            "Der KI-Assistent ist bereit, aber es wurde kein API-Schlüssel für "
            f"'{settings.LITELLM_MODEL}' konfiguriert. Bitte hinterlege einen "
            "GEMINI_API_KEY in den Umgebungsvariablen."
        )

    system_prompt = (
        "Du bist der hochkompetente 'BeeBoard KI-Assistent' für Imker.\n"
        "Deine Aufgabe ist es, dem Imker basierend auf seinen Daten präzise Auskunft "
        "zu geben. Antworte immer freundlich, sachlich und auf Deutsch. Halte dich kurz "
        "und hebe wichtige Warnungen (wie hohe Varroazahlen) hervor.\n\n"
        "Hier ist der aktuelle Zustand der Imkerei (Völker, Standorte, letzte Messungen):\n"
        f"{context_str}"
    )

    try:
        response = litellm.completion(
            model=settings.LITELLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            api_key=api_key
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LiteLLM error: {str(e)}")
        return f"Entschuldigung, es gab einen Fehler bei der Bearbeitung deiner Anfrage: {str(e)}"

def draft_entry_from_text(freetext: str, date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Uses the LLM to parse unstructured audio transcripts or notes
    and converts them into a structured JSON draft for a log entry.
    """
    if not date_str:
        date_str = date.today().isoformat()

    api_key = get_api_key_for_model(settings.LITELLM_MODEL)
    
    # Graceful fallback if no API key is set, so the app remains usable
    if not api_key and not settings.LITELLM_MODEL.startswith("ollama"):
        logger.warning("No API key configured for auto-drafting. Using rule-based fallback.")
        return get_fallback_draft(freetext, date_str)

    system_prompt = (
        "Du bist ein intelligenter Daten-Extraktor für Imker.\n"
        "Lies die folgende Freitext-Notiz des Imkers durch und wandle sie in ein valides JSON-Objekt um.\n"
        "Das JSON-Objekt MUSS exakt der folgenden Struktur entsprechen. Gib NUR das reine JSON zurück. Keine Markdowns wie ```json.\n\n"
        "STRUKTUR:\n"
        "{\n"
        "  \"hive_name\": \"Name des Volks (z.B. Volk 3) oder null wenn nicht genannt\",\n"
        "  \"entry_type\": \"Einer der Werte: 'INSPECTION', 'VARROA_COUNT', 'VARROA_TREATMENT', 'GENERAL'\",\n"
        "  \"notes\": \"Zusammenfassung der Notiz als Fließtext\",\n"
        "  \"date\": \"Datum im Format YYYY-MM-DD (Standard: '" + date_str + "')\",\n"
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

    try:
        response = litellm.completion(
            model=settings.LITELLM_MODEL,
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
