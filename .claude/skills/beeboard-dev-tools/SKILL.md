---
name: beeboard-dev-tools
description: Entwickler-Toolkit fuer BeeBoard 2 - Setup mit Poetry, Abhaengigkeiten verwalten, Backend und Frontend lokal starten, Stammdaten seeden, Daten aus BeeBoard 1 (Django) migrieren und Docker-Images bauen.
---

# BeeBoard 2 Developer Tools

Nutze diesen Skill, wenn du die Entwicklungsumgebung einrichtest, Abhaengigkeiten aenderst, die App lokal startest,
die Datenbank befuellst oder ein Docker-Image baust.

Alle Backend-Befehle laufen im Verzeichnis `backend/` ueber Poetry.

---

## 1. Setup

```bash
# Interaktiv (prueft Python + Poetry, poetry install, .env mit SECRET_KEY, optional GEMINI_API_KEY)
./scripts/setup.sh          # macOS / Linux / Git Bash
.\scripts\setup.ps1         # Windows PowerShell

# Manuell
cd backend
poetry install              # Runtime + Dev-Gruppe (pytest, ruff) nach backend/.venv
```

## 2. Abhaengigkeiten

```bash
poetry add <paket>                 # Runtime-Abhaengigkeit
poetry add --group dev <paket>     # Nur Entwicklung/Test
poetry remove <paket>
poetry lock                        # Lock-Datei nach manueller pyproject-Aenderung neu erzeugen
poetry show --outdated
```

`pyproject.toml` und `poetry.lock` immer gemeinsam committen. Kein `pip install` und keine `requirements.txt`.

## 3. Lokal starten

```bash
# Backend (in backend/)
poetry run alembic upgrade head
poetry run python -m app.scripts.seed
poetry run uvicorn app.main:app --reload --port 8000   # API-Doku: http://localhost:8000/docs

# Frontend (in frontend/)
npm install
npm run dev
```

## 4. Stammdaten seeden

`app/scripts/seed.py` legt Wabenmasse (`FrameType`, z.B. Zander, DeutschNormal, Langstroth), saisonale
Varroa-Multiplikatoren, Nummernkreise, Behandlungsmethoden und -anwendungsarten sowie Futtersorten an. Bestehende
Eintraege werden uebersprungen; das Schema kommt aus Alembic.

```bash
poetry run python -m app.scripts.seed
```

## 5. Datenmigration aus BeeBoard 1 (Django)

`app/scripts/migrate_django_data.py` importiert Benutzer, Bienenstaende, Standorte, Voelker und Logbuch aus der alten
SQLite-Datenbank. Erwarteter Quellpfad: `../beeboard/data/db.sqlite3` (Nachbar-Repository `beeboard`).

```bash
poetry run python -m app.scripts.migrate_django_data
```

Vorher ein Backup von `backend/data/beeboard.db` anlegen.

## 6. Quality-Gates

```bash
# backend/
poetry run ruff check app tests
poetry run pytest tests
# frontend/
npm run lint
npm run build
```

## 7. Docker

```bash
cd docker
docker compose up -d --build        # Unified-Image (Frontend + Backend + Nginx/HTTPS)
```

Die Dockerfiles installieren Abhaengigkeiten mit `poetry install --only main` in den System-Interpreter; nach einer
Abhaengigkeitsaenderung muss daher nur `poetry.lock` aktuell sein.
