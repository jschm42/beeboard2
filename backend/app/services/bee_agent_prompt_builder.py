"""
BeeAgentPromptBuilder

Assembles the system prompt for the Bee-Agent by combining:
- A master prompt template
- Scope-filtered apiary data (locations, hives, log entries)
- Optional weather data (if include_weather_data is True)
- A user-defined custom prompt suffix
"""
import json
import logging

from sqlalchemy.orm import Session

from app.models.bee_agent import BeeAgentJob

logger = logging.getLogger("beeboard.bee_agent")

class BeeAgentPromptTemplate:
    """Canonical Bee-Agent system prompt template (not user-editable)."""

    MASTER_SYSTEM_PROMPT = (
        "You are the highly competent 'BeeBoard Bee-Agent' – an autonomous beekeeping assistant.\n"
        "Analyze the following apiary data and generate a list of concrete, actionable tasks.\n\n"
        "OUTPUT FORMAT (STRICTLY REQUIRED):\n"
        "Return ONLY a JSON object. No Markdown wrappers, no explanatory text, just raw JSON.\n"
        "The object MUST follow this structure:\n"
        "{{\n"
        "  \"proposals\": [\n"
        "    {{\n"
        "      \"title\": \"Short, precise task title in the requested target language: {target_lang}\",\n"
        "      \"description\": \"Detailed reason/instructions in the requested target language: {target_lang}\",\n"
        "      \"priority\": \"HIGH|MEDIUM|LOW\",\n"
        "      \"due_date\": \"YYYY-MM-DD or null\",\n"
        "      \"location_id\": \"UUID of the location or null\",\n"
        "      \"hive_id\": \"UUID of the hive or null\"\n"
        "    }}\n"
        "  ]\n"
        "}}\n\n"
        "Rules:\n"
        "- ONLY generate tasks that are justified by the provided data.\n"
        "- Do NOT use placeholder UUIDs; only use actual IDs from the data, or null.\n"
        "- Prioritize urgent actions (e.g., high Varroa counts, swarm signs) as HIGH.\n"
        "- Return 0-10 tasks. If no action is needed, return an empty proposals array.\n"
    )


class BeeAgentPromptBuilder:
    """Builds the full system prompt for a BeeAgentJob run."""

    def __init__(self, job: BeeAgentJob, db: Session, lang: str = "de"):
        self._job = job
        self._db = db
        self._lang = lang

    async def build_system_prompt(self) -> str:
        """Assembles system prompt with scope-filtered context injected."""
        context_parts = [self._build_scope_context()]

        if self._job.include_journal_entries:
            context_parts.append(self._build_journal_context())

        if self._job.include_weather_data:
            weather_ctx = await self._build_weather_context()
            if weather_ctx:
                context_parts.append(weather_ctx)

        if self._job.include_tasks:
            context_parts.append(self._build_tasks_context())

        if self._job.include_calendar:
            context_parts.append(self._build_calendar_context())

        context_str = "\n\n".join(p for p in context_parts if p)

        target_lang_name = "German" if self._lang == "de" else "English"
        prompt_parts = [BeeAgentPromptTemplate.MASTER_SYSTEM_PROMPT.format(target_lang=target_lang_name)]
        if context_str:
            prompt_parts.append(f"=== CURRENT APIARY DATA ===\n{context_str}")
        if self._job.custom_prompt:
            prompt_parts.append(f"=== SPECIAL BEEKEEPER INSTRUCTIONS ===\n{self._job.custom_prompt.strip()}")

        return "\n\n".join(prompt_parts)

    async def _build_weather_context(self) -> str:
        from app.models.location import Location
        from app.services.weather import fetch_current_weather
        
        location_ids = self.get_scoped_location_ids()
        if not location_ids:
            return ""
            
        locations = self._db.query(Location).filter(Location.id.in_(location_ids)).all()
        lines = []
        for loc in locations:
            if loc.latitude is not None and loc.longitude is not None:
                try:
                    w = await fetch_current_weather(loc.latitude, loc.longitude)
                    if w:
                        temp = w.get("temp", 0.0)
                        humidity = w.get("humidity", 0)
                        wind = w.get("wind_speed", 0.0)
                        weather_desc = w.get("weather", [{}])[0].get("description", "Unknown")
                        lines.append(f"  - Location '{loc.name}': {temp}°C, {weather_desc}, Humidity: {humidity}%, Wind: {wind} m/s")
                except (RuntimeError, ValueError, TypeError) as exc:
                    logger.warning("Error fetching weather for location %s: %s", loc.id, exc)
        
        if lines:
            return "Current Weather:\n" + "\n".join(lines)
        return ""


    def get_scoped_location_ids(self) -> list[str]:
        """Returns location IDs relevant for this job based on its scope."""
        from app.models.location import Location
        from app.models.hive import Hive

        entity_ids = self._parse_entity_ids()

        if self._job.scope == "IMKEREI" or not entity_ids:
            locs = self._db.query(Location.id).filter(
                Location.apiary_id == self._job.apiary_id
            ).all()
            return [r[0] for r in locs]

        if self._job.scope == "STANDORT":
            return entity_ids

        if self._job.scope == "VOLK":
            # Derive locations from the selected hives
            hives = self._db.query(Hive).filter(Hive.id.in_(entity_ids)).all()
            loc_ids = list({h.location_id for h in hives if h.location_id})
            return loc_ids

        return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_entity_ids(self) -> list[str]:
        if not self._job.entity_ids:
            return []
        try:
            ids = json.loads(self._job.entity_ids)
            return [str(i) for i in ids] if isinstance(ids, list) else []
        except (ValueError, TypeError):
            return []

    def _build_scope_context(self) -> str:
        from app.models.location import Location
        from app.models.hive import Hive

        entity_ids = self._parse_entity_ids()
        lines: list[str] = []

        if self._job.scope == "IMKEREI" or not entity_ids:
            locations = self._db.query(Location).filter(
                Location.apiary_id == self._job.apiary_id
            ).all()
            hives = self._db.query(Hive).filter(
                Hive.apiary_id == self._job.apiary_id
            ).all()
        elif self._job.scope == "STANDORT":
            locations = self._db.query(Location).filter(
                Location.id.in_(entity_ids)
            ).all()
            hives = self._db.query(Hive).filter(
                Hive.location_id.in_(entity_ids)
            ).all()
        else:  # VOLK
            hives = self._db.query(Hive).filter(Hive.id.in_(entity_ids)).all()
            loc_ids = list({h.location_id for h in hives if h.location_id})
            locations = self._db.query(Location).filter(Location.id.in_(loc_ids)).all()

        if locations and self._job.include_locations:
            lines.append("Locations:")
            for loc in locations:
                lines.append(
                    f"  - ID={loc.id} Name='{loc.name}' Address='{loc.address}'"
                    + (f" Notes='{loc.notes}'" if loc.notes else "")
                )

        if hives and self._job.include_hives:
            lines.append("Colonies:")
            for hive in hives:
                status = "Active" if hive.is_active else "Inactive"
                queen = f"Queen from {hive.queen_year}" if hive.queen_year else "Queen year unknown"
                loc_name = hive.location.name if hive.location else "Unknown"
                lines.append(
                    f"  - ID={hive.id} Name='{hive.name}' ({status})"
                    f" Location='{loc_name}' {queen}"
                )

        return "\n".join(lines) if lines else ""

    def _build_journal_context(self) -> str:
        from app.models.logbook import LogEntry
        from app.models.hive import Hive
        from app.services.calculations import calculate_inspection_totals

        entity_ids = self._parse_entity_ids()
        limit = self._job.max_journal_entries or 20

        query = self._db.query(LogEntry).filter(
            LogEntry.apiary_id == self._job.apiary_id
        )

        if self._job.scope == "VOLK" and entity_ids:
            query = query.filter(LogEntry.hive_id.in_(entity_ids))
        elif self._job.scope == "STANDORT" and entity_ids:
            hive_ids = [
                r[0] for r in self._db.query(Hive.id).filter(
                    Hive.location_id.in_(entity_ids)
                ).all()
            ]
            if hive_ids:
                query = query.filter(LogEntry.hive_id.in_(hive_ids))

        entries = query.order_by(LogEntry.date.desc()).limit(limit).all()

        if not entries:
            return ""

        lines = [f"Recent hive log entries (max. {limit}):"]
        for entry in entries:
            detail = ""
            if entry.entry_type == "INSPECTION" and entry.inspection_detail:
                try:
                    totals = calculate_inspection_totals(entry.inspection_detail.boxes, self._db)
                    detail = (
                        f"Brood={totals.get('brood', 0)} frames,"
                        f" Food={totals.get('food', 0)} frames,"
                        f" Bees={totals.get('bees', 0)} frames"
                    )
                except (RuntimeError, ValueError, TypeError):
                    detail = "Inspection data parsing error"
            elif entry.entry_type == "VARROA_COUNT" and entry.varroa_count_detail:
                detail = (
                    f"Mite fall={entry.varroa_count_detail.raw_count},"
                    f" Estimated={entry.varroa_count_detail.estimated_total}"
                )
            elif entry.entry_type == "VARROA_TREATMENT" and entry.varroa_treatment_detail:
                detail = (
                    f"Treatment with {entry.varroa_treatment_detail.product}"
                    f" ({entry.varroa_treatment_detail.dosage})"
                )

            hive_name = entry.hive.name if entry.hive else "Unknown"
            lines.append(
                f"  - [{entry.date}] Hive='{hive_name}' Type={entry.entry_type} {detail}"
            )

        return "\n".join(lines)

    def _build_tasks_context(self) -> str:
        from app.models.task import Task
        from app.models.hive import Hive

        entity_ids = self._parse_entity_ids()
        query = self._db.query(Task).filter(
            Task.apiary_id == self._job.apiary_id,
            Task.is_completed == False
        )

        if self._job.scope == "VOLK" and entity_ids:
            query = query.filter(Task.hive_id.in_(entity_ids))
        elif self._job.scope == "STANDORT" and entity_ids:
            hive_ids = [
                r[0] for r in self._db.query(Hive.id).filter(
                    Hive.location_id.in_(entity_ids)
                ).all()
            ]
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Task.location_id.in_(entity_ids),
                    Task.hive_id.in_(hive_ids)
                )
            )

        tasks = query.all()
        if not tasks:
            return ""

        lines = ["Pending tasks:"]
        for t in tasks:
            due = f" (Due: {t.due_date})" if t.due_date else ""
            hive_name = t.hive.name if t.hive else "None"
            loc_name = t.location.name if t.location else "None"
            lines.append(f"  - [{t.priority}] {t.title}{due} (Location: {loc_name}, Hive: {hive_name})")
        return "\n".join(lines)

    def _build_calendar_context(self) -> str:
        from app.models.task import Task
        from app.models.hive import Hive

        entity_ids = self._parse_entity_ids()
        query = self._db.query(Task).filter(
            Task.apiary_id == self._job.apiary_id,
            Task.is_completed == False,
            Task.due_date.isnot(None)
        )

        if self._job.scope == "VOLK" and entity_ids:
            query = query.filter(Task.hive_id.in_(entity_ids))
        elif self._job.scope == "STANDORT" and entity_ids:
            hive_ids = [
                r[0] for r in self._db.query(Hive.id).filter(
                    Hive.location_id.in_(entity_ids)
                ).all()
            ]
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Task.location_id.in_(entity_ids),
                    Task.hive_id.in_(hive_ids)
                )
            )

        tasks = query.order_by(Task.due_date.asc()).all()
        if not tasks:
            return ""

        lines = ["Calendar events (Dues):"]
        for t in tasks:
            hive_name = t.hive.name if t.hive else "None"
            loc_name = t.location.name if t.location else "None"
            lines.append(f"  - Date={t.due_date} Type='Due task' Title='{t.title}' Priority='{t.priority}' (Location: {loc_name}, Hive: {hive_name})")
        return "\n".join(lines)
