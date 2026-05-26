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
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.bee_agent import BeeAgentJob

logger = logging.getLogger("beeboard.bee_agent")

MASTER_SYSTEM_PROMPT = (
    "Du bist der hochkompetente 'BeeBoard Bee-Agent' – ein autonomer Imker-Assistent.\n"
    "Analysiere die folgenden Imkerei-Daten und erstelle eine Liste konkreter, umsetzbarer Aufgaben.\n\n"
    "AUSGABEFORMAT (ZWINGEND einhalten):\n"
    "Gib ausschließlich ein JSON-Objekt zurück. Kein Markdown, kein erklärender Text, nur JSON.\n"
    "Das Objekt muss folgende Struktur haben:\n"
    "{\n"
    "  \"proposals\": [\n"
    "    {\n"
    "      \"title\": \"Kurzer, präziser Aufgabentitel\",\n"
    "      \"description\": \"Detaillierte Begründung/Anweisung auf Deutsch\",\n"
    "      \"priority\": \"HIGH|MEDIUM|LOW\",\n"
    "      \"due_date\": \"YYYY-MM-DD oder null\",\n"
    "      \"location_id\": \"UUID des Standorts oder null\",\n"
    "      \"hive_id\": \"UUID des Volks oder null\"\n"
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Regeln:\n"
    "- Erstelle NUR Aufgaben, die durch die vorliegenden Daten begründet sind.\n"
    "- Verwende KEINE placeholder-UUIDs; trage nur echte IDs aus den Daten ein, oder null.\n"
    "- Priorisiere dringende Maßnahmen (z.B. hohe Varroa, Schwarmzeichen) als HIGH.\n"
    "- Gib 0-10 Aufgaben zurück. Wenn keine Handlung erforderlich ist, gib ein leeres proposals-Array zurück.\n"
)


class BeeAgentPromptBuilder:
    """Builds the full system prompt for a BeeAgentJob run."""

    def __init__(self, job: BeeAgentJob, db: Session):
        self._job = job
        self._db = db

    def build_system_prompt(self) -> str:
        """Assembles system prompt with scope-filtered context injected."""
        context_parts = [self._build_scope_context()]

        if self._job.include_journal_entries:
            context_parts.append(self._build_journal_context())

        context_str = "\n\n".join(p for p in context_parts if p)

        prompt_parts = [MASTER_SYSTEM_PROMPT]
        if context_str:
            prompt_parts.append(f"=== AKTUELLE IMKEREI-DATEN ===\n{context_str}")
        if self._job.custom_prompt:
            prompt_parts.append(f"=== SPEZIELLE ANWEISUNG DES IMKERS ===\n{self._job.custom_prompt.strip()}")

        return "\n\n".join(prompt_parts)

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

        if locations:
            lines.append("Standorte:")
            for loc in locations:
                lines.append(
                    f"  - ID={loc.id} Name='{loc.name}' Adresse='{loc.address}'"
                    + (f" Notizen='{loc.notes}'" if loc.notes else "")
                )

        if hives:
            lines.append("Völker:")
            for hive in hives:
                status = "Aktiv" if hive.is_active else "Inaktiv"
                queen = f"Königin aus {hive.queen_year}" if hive.queen_year else "Königin-Jahr unbekannt"
                loc_name = hive.location.name if hive.location else "Unbekannt"
                lines.append(
                    f"  - ID={hive.id} Name='{hive.name}' ({status})"
                    f" Standort='{loc_name}' {queen}"
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

        lines = [f"Letzte Stockkarten-Einträge (max. {limit}):"]
        for entry in entries:
            detail = ""
            if entry.entry_type == "INSPECTION" and entry.inspection_detail:
                try:
                    totals = calculate_inspection_totals(entry.inspection_detail.boxes, self._db)
                    detail = (
                        f"Brut={totals.get('brood', 0)} Waben,"
                        f" Futter={totals.get('food', 0)} Waben,"
                        f" Bienen={totals.get('bees', 0)} Waben"
                    )
                except Exception:
                    detail = "Inspektionsdaten nicht auswertbar"
            elif entry.entry_type == "VARROA_COUNT" and entry.varroa_count_detail:
                detail = (
                    f"Milbenfall={entry.varroa_count_detail.raw_count},"
                    f" Geschätzt={entry.varroa_count_detail.estimated_total}"
                )
            elif entry.entry_type == "VARROA_TREATMENT" and entry.varroa_treatment_detail:
                detail = (
                    f"Behandlung {entry.varroa_treatment_detail.product}"
                    f" ({entry.varroa_treatment_detail.dosage})"
                )

            hive_name = entry.hive.name if entry.hive else "Unbekannt"
            lines.append(
                f"  - [{entry.date}] Volk='{hive_name}' Typ={entry.entry_type} {detail}"
            )

        return "\n".join(lines)
