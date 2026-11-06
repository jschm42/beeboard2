# BeeBoard 2 Agent Guidelines

Diese Datei ist der Einstiegspunkt fuer alle Coding-Agents (Claude Code, Copilot, Codex, Cursor, ...) und fuer
menschliche Entwickler. Sie nutzt Progressive Disclosure: Kernregeln stehen hier, Detailregeln und On-Demand-Skills
liegen unter `.claude/`.

> [!IMPORTANT]
> **Rules und Skills liegen in `.claude/`** (`.claude/rules/` und `.claude/skills/`). Das ist die einzige Quelle der
> Wahrheit fuer alle Agents. Claude Code laedt sie automatisch. Andere Agents (Copilot, Codex, Cursor, ...) muessen die
> passende Datei aus `.claude/` selbst lesen, sobald eine Regel oder ein Skill unten zutrifft.

---

## Kernregeln

1. **Zielbild**:
   - Schreibe wartbaren, testbaren und sicheren Code fuer BeeBoard 2.
   - Bevorzuge kleine, klar abgegrenzte Aenderungen statt grosser Refactorings ohne Auftrag.
   - Erhalte bestehende APIs, Datenmodelle und Router-Vertraege, wenn nicht explizit anders angefragt.

2. **Clean Code**:
   - Sprechende Namen, kurze Funktionen, klarer Kontrollfluss; fruehe Returns statt tiefer Verschachtelung.
   - Keine duplizierte Logik; wiederverwendbare Helfer in passende Module extrahieren.
   - Kommentare nur, wenn der Kontext sonst nicht offensichtlich ist.
   - Dateien konsistent zum bestehenden Stil im jeweiligen Verzeichnis halten.

3. **Aenderungsprinzipien**:
   - Minimal-invasive Aenderungen mit klarer Begruendung.
   - Bei Unsicherheit zuerst Annahmen offenlegen statt stillschweigend Verhalten zu aendern.
   - Breaking Changes nur mit expliziter Kennzeichnung und Migrationshinweis.

4. **Python-Abhaengigkeiten mit Poetry**:
   - Das Backend wird mit **Poetry 2.x** verwaltet (`backend/pyproject.toml`, `backend/poetry.lock`,
     virtuelle Umgebung `backend/.venv` laut `backend/poetry.toml`). Es gibt keine `requirements.txt` mehr.
   - Alle Backend-Befehle laufen im Verzeichnis `backend/` ueber `poetry run ...`.
   - Neue Abhaengigkeiten nur mit `poetry add <paket>` bzw. `poetry add --group dev <paket>`; `poetry.lock` immer
     mit committen.

5. **Qualitaets-Gates (Pflicht vor Abschluss jeder Aufgabe)**:
   - Backend (in `backend/`):

     ```bash
     poetry run ruff check app tests
     poetry run pytest tests
     ```

   - Frontend (in `frontend/`): `npm run lint` und `npm run build`.
   - Null Fehler, bevor eine Aufgabe als erledigt gilt.

6. **Dokumentation synchron halten**:
   - Aenderungen an Setup, Befehlen, APIs oder fachlichen Regeln aktualisieren im selben Schritt `README.md`, die
     betroffenen `.claude/rules/` und `.claude/skills/`.

---

## 1. Workspace Rules (`.claude/rules/`)

Projektregeln liegen in `.claude/rules/` und werden kontextabhaengig geladen:

- [architecture.md](.claude/rules/architecture.md) (`trigger: model_decision`) — Schichtung Router → Services →
  Models, Schemas, Alembic, Frontend-Aufbau (Vue 3, Pinia, i18n), MCP-Server.
- [python.md](.claude/rules/python.md) (`trigger: glob`, `backend/**/*.py`) — Python-Konventionen, Poetry, Ruff,
  Fehlerbehandlung, Alembic-Migrationen.
- [frontend.md](.claude/rules/frontend.md) (`trigger: glob`, `frontend/**/*.{js,vue}`) — Views/Komponenten, Pinia-Stores,
  API-Aufrufe, i18n (`de.json`/`en.json`).
- [testing.md](.claude/rules/testing.md) (`trigger: glob`, `backend/tests/**/*.py`) — pytest, In-Memory-SQLite,
  Fixtures, keine echten LLM-/Netzwerkaufrufe.
- [security.md](.claude/rules/security.md) (`trigger: model_decision`) — Secrets, Eingabevalidierung, AuthN/AuthZ,
  Imkerei-Zugriffsrechte, Logging.
- [hive-inspection.md](.claude/rules/hive-inspection.md) (`trigger: model_decision`) — Beuteninspektion nach der
  Achtel-Schaetzmethode (Multiplikatoren je Wabenmass).

---

## 2. On-Demand Skills (`.claude/skills/`)

Jeder Skill ist ein Ordner mit einer `SKILL.md`. Vor der jeweiligen Aufgabe lesen.

- [beeboard-dev-tools](.claude/skills/beeboard-dev-tools/SKILL.md) — Setup mit Poetry, Backend/Frontend starten,
  Seeding, Django-Datenmigration, Docker-Build.
- [beeboard-db-migrations](.claude/skills/beeboard-db-migrations/SKILL.md) — Alembic-Migrationen anlegen, pruefen,
  Heads mergen.
- [beeboard-mcp-server](.claude/skills/beeboard-mcp-server/SKILL.md) — BeeBoard-MCP-Server starten, in Clients
  einbinden und neue Tools ergaenzen.

---

## 3. Agent-freundliche Befehlsausfuehrung

- **Keine Pager:** Git-Befehle immer mit `--no-pager` ausfuehren (z.B. `git --no-pager diff`).
- **Keine Token-Flut:** Grosse Dateien nicht komplett ausgeben; gezielt lesen (`head -n 50 <datei>`, Suche).
- **Poetry statt pip:** Niemals `pip install` im Projekt-Venv; immer `poetry add` / `poetry install`.
