---
name: beeboard-db-migrations
description: Alembic-Migrationen fuer BeeBoard 2 anlegen, pruefen und anwenden - neue Tabellen/Spalten, Datenmigrationen, mehrere Heads mergen und Downgrades testen.
---

# BeeBoard 2 Datenbank-Migrationen (Alembic)

Nutze diesen Skill bei jeder Aenderung an `backend/app/models/`. Jede Schemaaenderung braucht eine Migration in
`backend/alembic/versions/`; die App aendert das Schema nie selbst.

Alle Befehle im Verzeichnis `backend/`.

---

## 1. Status pruefen

```bash
poetry run alembic current
poetry run alembic heads     # muss genau einen Head zeigen
poetry run alembic history -r -3:
```

## 2. Migration anlegen

```bash
# Modell in app/models/ aendern, dann:
poetry run alembic revision --autogenerate -m "add_<feature>_to_<table>"
```

Danach die erzeugte Datei **immer pruefen**:

* Nur die beabsichtigten Aenderungen enthalten? Autogenerate erkennt keine Umbenennungen (Drop + Add).
* SQLite: Spaltenaenderungen an bestehenden Tabellen mit `op.batch_alter_table(...)` schreiben.
* Neue `NOT NULL`-Spalten brauchen einen `server_default` oder eine Datenmigration fuer bestehende Zeilen.
* `downgrade()` muss die Aenderung sauber zuruecknehmen.
* Neue Modelle muessen in `app/models/__init__.py` importiert sein, sonst sieht Autogenerate sie nicht.

## 3. Anwenden und testen

```bash
poetry run alembic upgrade head
poetry run alembic downgrade -1 && poetry run alembic upgrade head   # Roundtrip
poetry run pytest tests
```

Fuer neue Stammdaten zusaetzlich `app/scripts/seed.py` erweitern (idempotent).

## 4. Mehrere Heads mergen

Entstehen durch parallele Branches mehrere Heads:

```bash
poetry run alembic merge -m "merge_heads" <rev_a> <rev_b>
poetry run alembic upgrade head
```
