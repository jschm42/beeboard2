---
description: Teststandards fuer das BeeBoard-Backend - pytest ueber Poetry, In-Memory-SQLite-Fixtures, AAA-Muster, keine echten LLM- oder Netzwerkaufrufe.
trigger: glob
globs: "backend/tests/**/*.py"
paths:
  - "backend/tests/**/*.py"
---

# Testing Guidelines

1. **Ausfuehrung**: In `backend/` mit `poetry run pytest tests` (einzelne Datei: `poetry run pytest tests/test_x.py`).
2. **Struktur**: Arrange, Act, Assert. Neue Endpunkte und Berechnungen (`services/calculations.py`) bekommen Tests.
3. **Fixtures** (`tests/conftest.py`):
   * `db`: Session auf In-Memory-SQLite mit Rollback pro Test; Stammdaten sind per `seed_database` vorhanden.
   * `client`: FastAPI-`TestClient` mit ueberschriebenem `get_db`.
   * Bestehende Fixtures wiederverwenden statt eigene DB-Setups zu bauen.
4. **Mocking**: **Keine echten Netzwerk- oder LLM-Aufrufe** (litellm, Wetter-API, Geocoding). Mit
   `unittest.mock.patch` mocken.
5. **Berechtigungen**: Fuer geschuetzte Endpunkte auch den Fall "fremder Benutzer / keine Mitgliedschaft" testen.
