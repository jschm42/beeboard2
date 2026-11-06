---
description: BeeBoard 2 Architektur - Schichtung Router/Services/Models/Schemas, Alembic, Frontend (Vue 3, Pinia, i18n) und MCP-Server.
trigger: model_decision
---

# BeeBoard 2 Architektur

## 1. Backend (`backend/app/`, FastAPI, Python 3.13, Poetry)

| Paket | Inhalt |
| --- | --- |
| `routers/` | HTTP-Schicht: Request/Response, Permissions, Statuscodes. Keine Business-Logik. |
| `services/` | Business-Logik (z.B. `calculations.py`, `ai_assistant.py`, `cron.py`, `pdf_export.py`, `weather.py`). |
| `models/` | SQLAlchemy-Modelle (Persistenz). |
| `schemas/` | Pydantic-Schemas (API-Vertraege). |
| `core/` | `config.py` (Settings), `database.py` (Session, `get_db`), `security.py` (JWT, `get_current_user`). |
| `scripts/` | CLI-Skripte: `seed.py` (Stammdaten), `migrate_django_data.py` (Import aus BeeBoard 1). |
| `mcp_server.py` | FastMCP-Server "BeeBoard" fuer externe Agents. |

Regeln:

* Schichtung einhalten: **Router → Services → Models**. Abhaengigkeiten zeigen nur in diese Richtung.
* Business-Logik gehoert in Services, nicht in Router.
* DB-Schema nur ueber Alembic-Migrationen aendern (`backend/alembic/versions/`, Skill `beeboard-db-migrations`).
  Die Anwendung fuehrt beim Start kein `ALTER TABLE` aus.
* Konfiguration nur ueber `app.core.config.Settings` (Umgebungsvariablen / `.env`).
* Abhaengigkeiten werden mit Poetry verwaltet (`backend/pyproject.toml`); Docker installiert sie mit
  `poetry install --only main` in den System-Interpreter.

## 2. Frontend (`frontend/src/`, Vue 3 + Vite + Tailwind)

* `views/` orchestrieren eine Seite; `components/` kapseln Darstellung und Interaktion.
* State liegt in Pinia-Stores (`stores/`); API-Aufrufe zentral und nachvollziehbar (axios).
* Texte ueber `vue-i18n` (`locales/de.json`, `locales/en.json`), immer beide Sprachen pflegen.
* Der Vite-Dev-Server proxyt `/api` und `/uploads` auf das Backend (`http://localhost:8000`).

## 3. Deployment (`docker/`)

* `Dockerfile.unified`: Frontend-Build + Backend + Nginx (HTTPS) in einem Container; `docker-compose.yml` nutzt ihn.
* `Dockerfile.backend`: reines Backend.
* Entrypoints fuehren `alembic upgrade head` und `python -m app.scripts.seed` aus.
