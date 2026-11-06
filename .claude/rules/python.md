---
description: Python-Konventionen fuer das BeeBoard-Backend - Poetry, Ruff, Typisierung, Fehlerbehandlung und Alembic-Migrationen.
trigger: glob
globs: "backend/**/*.py"
paths:
  - "backend/**/*.py"
---

# Python Guidelines

1. **Umgebung & Abhaengigkeiten**:
   * Alle Befehle im Verzeichnis `backend/` ueber Poetry ausfuehren (`poetry run ...`).
   * Abhaengigkeiten nur mit `poetry add` / `poetry add --group dev` aendern und `poetry.lock` mit committen.
2. **Naming**:
   * `PascalCase` fuer Klassen und Pydantic-Modelle, `snake_case` fuer Funktionen, Variablen und Module,
     `UPPER_SNAKE_CASE` fuer Modulkonstanten.
3. **Typisierung**: Type Hints fuer Funktionsparameter und Rueckgabewerte verwenden.
4. **Single Responsibility**:
   * Funktionen, Services und Router fokussiert halten; grosse Funktionen in kleine, testbare Helfer zerlegen.
   * Router (HTTP-Mapping, Validierung) von Business-Logik, DB-Abfragen und externen Aufrufen trennen.
5. **Fehlerbehandlung**:
   * Keine leeren `except`-Bloecke; Ausnahmen loggen oder behandeln.
   * In FastAPI-Endpunkten `HTTPException` mit passendem Statuscode (400, 403, 404, ...) und nutzersicherer Meldung.
6. **Datenbank**:
   * Nur SQLAlchemy ORM/Core mit parametrisierten Queries; kein String-SQL mit Nutzereingaben.
   * Jede Schemaaenderung braucht eine Alembic-Migration (siehe Skill `beeboard-db-migrations`).
7. **Linting**: Vor Abschluss `poetry run ruff check app tests` ohne Fehler. Ruff-Konfiguration steht in
   `backend/pyproject.toml`.
