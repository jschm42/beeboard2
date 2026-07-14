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
from app.models.user import User

logger = logging.getLogger("beeboard.ai")

DEFAULT_CHATBOT_PROMPT = (
    "You are the highly competent 'BeeBoard AI Assistant' for beekeepers.\n"
    "Your job is to provide precise information based on the beekeeper's data.\n"
    "Always reply in a friendly, professional manner. Respond in the requested target language: {target_lang}.\n"
    "Keep your answers concise and highlight important warnings (like high varroa counts).\n\n"
    "Here is the current state of the apiary (hives, locations, recent measurements):\n"
    "{context_str}"
)

DEFAULT_DRAFT_PROMPT = (
    "You are an intelligent data extractor for beekeepers.\n"
    "Read the following free-text note from the beekeeper and convert it into a valid JSON object.\n"
    "The JSON object MUST exactly match the following structure. Return ONLY the raw JSON string. Do NOT wrap it in markdown code fences like ```json.\n\n"
    "STRUCTURE:\n"
    "{\n"
    "  \"hive_name\": \"Name of the colony/hive (e.g., Volk 3 or Hive 3), or null if not mentioned\",\n"
    "  \"entry_type\": \"One of: 'INSPECTION', 'VARROA_COUNT', 'GENERAL'\",\n"
    "  \"notes\": \"Summary of the note in the requested target language: {target_lang}\",\n"
    "  \"date\": \"Date in YYYY-MM-DD format (default: '{date_str}')\",\n"
    "  \"inspection_detail\": {\n"
    "    \"frames\": [\n"
    "      {\n"
    "        \"frame_number\": 1, // Number of the frame (1-based)\n"
    "        \"side\": 1,         // Frame side (1 or 2)\n"
    "        \"brood_eighths\": 0, // Brood in eighths (0-8)\n"
    "        \"food_eighths\": 0,  // Food in eighths (0-8)\n"
    "        \"bee_eighths\": 0    // Bee mass in eighths (0-8)\n"
    "      }\n"
    "    ]\n"
    "  }, // Present only if entry_type = 'INSPECTION', otherwise null\n"
    "  \"varroa_count_detail\": {\n"
    "    \"raw_count\": 0 // Raw count of varroa mites (integer)\n"
    "  } // Present only if entry_type = 'VARROA_COUNT', otherwise null\n"
    "}"
)

DEFAULT_HONEY_DRAFT_PROMPT = (
    "You are an intelligent data extractor for beekeepers.\n"
    "Read the following free-text note from the beekeeper and convert it into a valid JSON object for a Honey Batch.\n"
    "The JSON object MUST exactly match the following structure. Return ONLY the raw JSON string. Do NOT wrap it in markdown code fences like ```json.\n\n"
    "IMPORTANT for 'honey_type': Prefer using one of these standard or D.I.B.-compliant German/English names based on the note:\n"
    "- 'Akazienhonig / Robinienhonig' (Acacia Honey), 'Edelkastanienhonig' (Chestnut Honey), 'Lindenhonig' (Linden Honey), 'Löwenzahnhonig' (Dandelion Honey), 'Rapshonig' (Rape Honey), 'Waldhonig' (Forest Honey), 'Blütenhonig' (Flower Honey), etc.\n"
    "If a specific custom type or regional detail is mentioned, use it. Write the 'notes' field in the requested target language: {target_lang}.\n\n"
    "STRUCTURE:\n"
    "{\n"
    "  \"batch_number\": \"Lot/Batch number (e.g., L123-2026), null if not mentioned\",\n"
    "  \"honey_type\": \"Honey type, default 'Flower Honey' or 'Blütenhonig' if not mentioned\",\n"
    "  \"harvest_date\": \"Harvest date in YYYY-MM-DD format (default: '{date_str}')\",\n"
    "  \"bottling_date\": \"Bottling date in YYYY-MM-DD format or null\",\n"
    "  \"quantity_kg\": Quantity in kilograms as float (e.g., 45.5), default 0.0,\n"
    "  \"water_content_percent\": Water content in percent as float (e.g., 16.2) or null,\n"
    "  \"heating_temperature_celsius\": Heating temperature in Celsius as float (e.g., 35.0) or null,\n"
    "  \"best_before_date\": \"Best before date in YYYY-MM-DD format (default: 2 years after harvest_date, e.g. '{bb_date_str}')\",\n"
    "  \"is_exact_date\": true/false, // true if an exact best before date was specified in the text, otherwise false,\n"
    "  \"dib_label_start\": \"Start number of D.I.B. seal or null\",\n"
    "  \"dib_label_end\": \"End number of D.I.B. seal or null\",\n"
    "  \"reserve_sample_taken\": true/false, // true if a reserve sample was taken, otherwise false,\n"
    "  \"reserve_sample_date\": \"Date reserve sample was taken in YYYY-MM-DD format or null\",\n"
    "  \"reserve_sample_id\": \"ID/Number of the reserve sample or null\",\n"
    "  \"notes\": \"Other notes or remarks in the requested target language: {target_lang}\"\n"
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
            currency="EUR",
            tax_rates="0.0,7.0,19.0",
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    else:
        changed = False
        if not config.ai_insights_cron:
            config.ai_insights_cron = "0 */12 * * *"
            changed = True
        if not config.currency:
            config.currency = "EUR"
            changed = True
        if not config.tax_rates:
            config.tax_rates = "0.0,7.0,19.0"
            changed = True
        if changed:
            db.commit()
            db.refresh(config)
    return config

async def run_agent_loop(system_prompt: str, user_prompt: str, db: Session, apiary_id: str, current_user: Optional[User] = None, effective_model: str = "", api_key: str = "", lang: str = "de") -> str:
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
    
    config = get_llm_config(db)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_locations",
                "description": "Downloads all locations of the current apiary.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_hives",
                "description": "Downloads all colonies/hives (name, status, queen, boxes) of the apiary.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_recent_log_entries",
                "description": "Downloads logbook entries and diagnostics (inspections, varroa count, treatment) of the last N days.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "description": "Number of days in the past to query (default: 7)"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "log_honey_sale",
                "description": "Records a new honey sale for the current user in the database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string", "description": "Name or type of the product (e.g. 'Rape Honey', 'Linden Honey 500g')"},
                        "quantity": {"type": "number", "description": "Quantity sold (number of jars or kg)"},
                        "total_price": {"type": "number", "description": "Total price in Euros for the given quantity (e.g. 18.0)"},
                        "sales_channel": {"type": "string", "enum": ["direktverkauf", "online", "email", "verkaufsstand"], "description": "Sales channel"},
                        "batch_number": {"type": "string", "description": "The lot/batch number (e.g. 'L-02' or 'LOT-0001'), if available"},
                        "notes": {"type": "string", "description": "Additional notes about the sale, optional"}
                    },
                    "required": ["product_name", "quantity", "total_price", "sales_channel"]
                }
            }
        }
    ]
    
    if config.enable_weather_api:
        tools.append({
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Downloads current weather for all locations of the apiary (via OpenWeatherMap).",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        })
    
    for _ in range(5):
        try:
            response = await litellm.acompletion(
                model=effective_model,
                messages=messages,
                tools=tools,
                api_key=api_key
            )
        except Exception as e:
            logger.exception("LiteLLM completion error")
            return "Fehler bei der KI-Anfrage. Bitte versuche es später erneut." if lang == "de" else "AI request error. Please try again later."
            
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
                    res = [f"Location '{loc.name}' in {loc.address}. Notes: {loc.notes or 'None'}" for loc in locations]
                    result = "\n".join(res) if res else "No locations found."
                    
                elif function_name == "get_hives":
                    hives = db.query(Hive).filter(Hive.apiary_id == apiary_id).all()
                    res = []
                    for hive in hives:
                        status_str = "Active" if hive.is_active else "Inactive"
                        queen_str = f"Queen from {hive.queen_year}" if hive.queen_year else "Queen year unknown"
                        boxes_str = f"{len(hive.boxes)} boxes"
                        res.append(f"- Colony '{hive.name}' ({status_str}): Location='{hive.location.name if hive.location else 'Unknown'}', {queen_str}, Structure={boxes_str}.")
                    result = "\n".join(res) if res else "No colonies found."
                    
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
                            totals = calculate_inspection_totals(entry.inspection_detail.boxes, db)
                            detail_desc = f"Brood={totals.get('brood',0)} frames, Food={totals.get('food',0)} frames, Bees={totals.get('bees',0)} frames"
                        elif entry.entry_type == "VARROA_COUNT" and entry.varroa_count_detail:
                            detail_desc = f"Mite fall={entry.varroa_count_detail.raw_count}, Estimated={entry.varroa_count_detail.estimated_total}"
                        elif entry.entry_type == "VARROA_TREATMENT" and entry.varroa_treatment_detail:
                            detail_desc = f"Treatment {entry.varroa_treatment_detail.product} ({entry.varroa_treatment_detail.dosage})"
                        res.append(f"- [{entry.date}] Hive: '{entry.hive.name if entry.hive else 'Unknown'}' | Type: {entry.entry_type} | Details: {detail_desc}")
                    result = "\n".join(res) if res else f"No log entries found in the last {days} days."
                    
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
                                weather_desc = w.get("weather", [{}])[0].get("description", "Unknown")
                                res.append(f"Location '{loc.name}': {temp}°C, {weather_desc}, Humidity: {humidity}%, Wind: {wind} m/s")
                    result = "\n".join(res) if res else "Could not retrieve weather data (or no geodata)."
                elif function_name == "log_honey_sale":
                    if not current_user:
                        result = "Error: No active user context found to log sales."
                    else:
                        product_name = arguments.get("product_name")
                        quantity = float(arguments.get("quantity", 0))
                        total_price = float(arguments.get("total_price", 0))
                        sales_channel = arguments.get("sales_channel", "direktverkauf")
                        batch_number = arguments.get("batch_number")
                        notes = arguments.get("notes")

                        # Map channel
                        channel_map = {
                            "direktverkauf": "direktverkauf",
                            "direkt": "direktverkauf",
                            "online": "online",
                            "email": "email",
                            "e-mail": "email",
                            "verkaufsstand": "verkaufsstand",
                            "stand": "verkaufsstand"
                        }
                        sales_channel = channel_map.get(str(sales_channel).lower(), "direktverkauf")

                        from app.models.sales import ProductConfig, HoneySale
                        from app.models.honey_batch import HoneyBatch

                        # Look up product config
                        products = db.query(ProductConfig).filter(ProductConfig.created_by_id == current_user.id).all()
                        matched_product = None
                        for p in products:
                            if product_name.lower() in p.name.lower() or p.name.lower() in product_name.lower() or product_name.lower() in p.honey_type.lower():
                                matched_product = p
                                break

                        # Proactive creation if no product matches
                        if not matched_product:
                            tax = 7.0
                            if "met" in product_name.lower() or "honigwein" in product_name.lower():
                                tax = 19.0
                            unit_price = total_price / quantity if quantity > 0 else 6.0
                            matched_product = ProductConfig(
                                name=product_name,
                                honey_type=product_name,
                                price=unit_price,
                                tax_rate=tax,
                                is_active=True,
                                created_by_id=current_user.id
                            )
                            db.add(matched_product)
                            db.commit()
                            db.refresh(matched_product)
                            notes_extra = f" (Product '{product_name}' was automatically created)"
                        else:
                            notes_extra = ""

                        # Look up batch
                        batch = None
                        if batch_number:
                            batch = db.query(HoneyBatch).filter(
                                HoneyBatch.batch_number == batch_number
                            ).first()
                            if not batch:
                                batch = db.query(HoneyBatch).filter(
                                    HoneyBatch.batch_number.contains(batch_number)
                                ).first()

                        # Save sale
                        new_sale = HoneySale(
                            sale_date=datetime.now(),
                            product_id=matched_product.id,
                            batch_id=batch.id if batch else None,
                            quantity=quantity,
                            total_price=total_price,
                            sales_channel=sales_channel,
                            notes=(notes or "") + notes_extra,
                            created_by_id=current_user.id
                        )
                        db.add(new_sale)
                        db.commit()
                        db.refresh(new_sale)

                        result = f"Successfully logged: {quantity}x '{matched_product.name}' for {total_price}€ via channel '{sales_channel}'."
                        if batch:
                            result += f" Linked with batch '{batch.batch_number}'."
                else:
                    result = f"Unknown function: {function_name}"
            except Exception as e:
                result = f"Error executing function: {str(e)}"
                
            messages.append({
                "role": "tool",
                "name": function_name,
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
            
    return "Der Assistent konnte die Anfrage nicht innerhalb der maximalen Anzahl von Schritten beantworten." if lang == "de" else "The assistant could not answer the request within the maximum number of steps."


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

async def chatbot_completion(query: str, apiary_id: str, current_user: User, db: Session, lang: str = "de") -> str:
    """
    Sends the user query along with tool access to the LLM
    to generate helpful, context-aware advice for the beekeeper.
    """
    effective_model, api_key = get_effective_model_and_key(settings.LITELLM_MODEL)
    
    # If no API key is provided, gracefully inform the user or fall back
    if not api_key and not effective_model.startswith("ollama"):
        if lang == "de":
            return (
                "Der KI-Assistent ist bereit, aber es wurde kein API-Schlüssel für "
                f"'{settings.LITELLM_MODEL}' konfiguriert. Bitte hinterlege einen "
                "passenden API-Schlüssel (z.B. GEMINI_API_KEY, OPENROUTER_API_KEY, ANTHROPIC_API_KEY) in den Umgebungsvariablen."
            )
        else:
            return (
                "The AI assistant is ready, but no API key has been configured for "
                f"'{settings.LITELLM_MODEL}'. Please configure a "
                "valid API key (e.g. GEMINI_API_KEY, OPENROUTER_API_KEY, ANTHROPIC_API_KEY) in your environment variables."
            )

    config = get_llm_config(db)
    
    # Use English tool description reminder in the system prompt injection
    system_prompt = config.chatbot_system_prompt.replace(
        "{context_str}", 
        "You have access to tools to fetch all needed data (weather, logbook, colonies, locations) yourself and book sales directly. Use them!"
    )
    
    target_lang_name = "German" if lang == "de" else "English"
    if "{target_lang}" in system_prompt:
        system_prompt = system_prompt.replace("{target_lang}", target_lang_name)
    else:
        system_prompt += f"\n\nIMPORTANT: Respond in the requested target language: {target_lang_name}."

    try:
        return await run_agent_loop(system_prompt, query, db, apiary_id, current_user, effective_model, api_key, lang=lang)
    except Exception as e:
        logger.exception("LiteLLM error")
        return "Entschuldigung, es gab einen internen Fehler bei der Bearbeitung deiner Anfrage." if lang == "de" else "Sorry, there was an internal error processing your request."

def draft_entry_from_text(freetext: str, date_str: Optional[str] = None, db: Optional[Session] = None, lang: str = "de") -> Dict[str, Any]:
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
    target_lang_name = "German" if lang == "de" else "English"
    if "{target_lang}" in system_prompt:
        system_prompt = system_prompt.replace("{target_lang}", target_lang_name)
    else:
        system_prompt += f"\n\nIMPORTANT: Write the 'notes' field in the requested target language: {target_lang_name}."

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
        return get_fallback_draft(freetext, date_str)

def get_fallback_draft(freetext: str, date_str: str, error: Optional[str] = None) -> Dict[str, Any]:
    """Generates a structured dictionary from text if LLM extraction fails or is unconfigured."""
    text_lower = freetext.lower()
    
    # Basic rule-based classification for seamless UX without AI keys
    entry_type = "GENERAL"
    if "milben" in text_lower or "varroa" in text_lower or "zählung" in text_lower or "gezählt" in text_lower:
        if not ("behandlung" in text_lower or "behandelt" in text_lower or "präparat" in text_lower):
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

    draft = {
        "hive_name": hive_name,
        "entry_type": entry_type,
        "notes": notes,
        "date": date_str,
        "inspection_detail": None,
        "varroa_count_detail": None
    }

    if entry_type == "VARROA_COUNT":
        draft["varroa_count_detail"] = {"raw_count": raw_count}
    elif entry_type == "INSPECTION":
        draft["inspection_detail"] = {"frames": []}

    return draft

def get_fallback_honey_draft(freetext: str, harvest_date_str: str, error: Optional[str] = None) -> Dict[str, Any]:
    """Generates a structured honey batch dictionary from text if LLM extraction fails or is unconfigured."""
    text_lower = freetext.lower()
    
    # Try to find honey types
    honey_type = "Blütenhonig"
    for t in ["frühjahr", "sommer", "raps", "linde", "wald", "tanne", "heide", "kastanie", "blüte"]:
        if t in text_lower:
            if t == "frühjahr": honey_type = "Frühjahrsblütenhonig"
            elif t == "sommer": honey_type = "Sommerblütenhonig"
            elif t == "raps": honey_type = "Rapshonig"
            elif t == "linde": honey_type = "Lindenhonig"
            elif t == "wald": honey_type = "Waldhonig"
            elif t == "tanne": honey_type = "Tannenhonig"
            elif t == "heide": honey_type = "Heidehonig"
            elif t == "blüte": honey_type = "Blütenhonig"
            break
            
    # Try to find quantity (kg)
    quantity = 0.0
    words = text_lower.split()
    for idx, w in enumerate(words):
        if "kg" in w or "kilo" in w:
            if idx > 0:
                prev = words[idx-1].replace(",", ".")
                try:
                    quantity = float(prev)
                    break
                except ValueError:
                    pass
        elif w.replace(",", ".").replace("kg", "").replace("kilo", "").replace(".", "", 1).isdigit():
            val = w.replace("kg", "").replace("kilo", "").replace(",", ".")
            try:
                quantity = float(val)
                break
            except ValueError:
                pass

    # Try to find water content (%)
    water = None
    for idx, w in enumerate(words):
        if "%" in w or "wasser" in w:
            if idx > 0:
                prev = words[idx-1].replace(",", ".")
                try:
                    water = float(prev)
                    break
                except ValueError:
                    pass
            val = w.replace("%", "").replace("wasser", "").replace(",", ".")
            try:
                water = float(val)
                break
            except ValueError:
                pass

    # Reserve sample
    sample_taken = "probe" in text_lower or "rückstell" in text_lower or "rückstellprobe" in text_lower

    notes = freetext
    if error:
        notes += f"\n\n(Hinweis: KI-Extraktion fehlgeschlagen - {error})"

    # default BB date is 2 years from today
    from datetime import datetime, timedelta
    try:
        harvest_dt = date.fromisoformat(harvest_date_str)
    except ValueError:
        harvest_dt = date.today()
    bb_dt = harvest_dt + timedelta(days=730)
    
    return {
        "batch_number": None,
        "honey_type": honey_type,
        "harvest_date": harvest_date_str,
        "bottling_date": None,
        "quantity_kg": quantity,
        "water_content_percent": water,
        "heating_temperature_celsius": None,
        "best_before_date": bb_dt.isoformat(),
        "is_exact_date": False,
        "dib_label_start": None,
        "dib_label_end": None,
        "reserve_sample_taken": sample_taken,
        "reserve_sample_date": harvest_date_str if sample_taken else None,
        "reserve_sample_id": None,
        "notes": notes
    }

def draft_honey_batch_from_text(freetext: str, harvest_date_str: Optional[str] = None, db: Optional[Session] = None, lang: str = "de") -> Dict[str, Any]:
    """
    Uses the LLM to parse unstructured honey harvest or bottling notes
    and converts them into a structured JSON draft for a honey batch.
    """
    if not harvest_date_str:
        harvest_date_str = date.today().isoformat()

    effective_model, api_key = get_effective_model_and_key(settings.LITELLM_MODEL)
    
    if not api_key and not effective_model.startswith("ollama"):
        logger.warning("No API key configured for honey auto-drafting. Using rule-based fallback.")
        return get_fallback_honey_draft(freetext, harvest_date_str)

    try:
        harvest_dt = date.fromisoformat(harvest_date_str)
    except ValueError:
        harvest_dt = date.today()
    from datetime import timedelta
    bb_dt = harvest_dt + timedelta(days=730)
    bb_date_str = bb_dt.isoformat()

    prompt_tmpl = DEFAULT_HONEY_DRAFT_PROMPT
    system_prompt = prompt_tmpl.replace("{date_str}", harvest_date_str).replace("{bb_date_str}", bb_date_str)
    target_lang_name = "German" if lang == "de" else "English"
    if "{target_lang}" in system_prompt:
        system_prompt = system_prompt.replace("{target_lang}", target_lang_name)
    else:
        system_prompt += f"\n\nIMPORTANT: Write the 'notes' field in the requested target language: {target_lang_name}."

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
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        return json.loads(content)
    except Exception as e:
        logger.error(f"LiteLLM honey auto-draft error: {str(e)}")
        return get_fallback_honey_draft(
            freetext,
            harvest_date_str,
            error="KI-Extraktion fehlgeschlagen. Fallback-Entwurf wurde erstellt."
        )
