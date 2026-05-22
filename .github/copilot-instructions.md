# BeeBoard 2 Copilot Instructions

## Zielbild

- Schreibe wartbaren, testbaren und sicheren Code fuer BeeBoard 2.
- Bevorzuge kleine, klar abgegrenzte Aenderungen statt grosser Refactorings ohne Auftrag.
- Erhalte bestehende APIs, Datenmodelle und Router-Vertraege, wenn nicht explizit anders angefragt.

## Clean Code

- Verwende sprechende Namen, kurze Funktionen und klaren Kontrollfluss.
- Vermeide duplizierte Logik; extrahiere wiederverwendbare Helfer in passende Module.
- Nutze fruehe Returns statt tiefer Verschachtelung.
- Schreibe nur Kommentare, wenn der Kontext sonst nicht offensichtlich ist.
- Halte Dateien konsistent zum bestehenden Stil im jeweiligen Verzeichnis.
- Fuehre bei Aenderungen immer relevante Tests und Linter aus.

## Security

- Niemals Secrets, Tokens, API Keys oder personenbezogene Daten hardcoden.
- Nutze Umgebungsvariablen ueber `backend/app/core/config.py`.
- Validiere alle API-Eingaben ueber Pydantic-Schemas und defensive Checks.
- Erzwinge Authentifizierung/Autorisierung in Routern fuer geschuetzte Endpunkte.
- Vermeide SQL-Injection-Risiken: nur SQLAlchemy-ORM/Core mit parametrisierten Queries.
- Logge keine sensiblen Daten (Passwoerter, Tokens, persoenliche Inhalte).
- Bevorzuge sichere Standardwerte (deny by default, least privilege, fail closed).

## Architektur

- Folge der Schichtung:
  - Router: HTTP, Request/Response, Permissions
  - Services: Business-Logik
  - Models: Persistenz
  - Schemas: API-Vertraege
- Keine Business-Logik in Routern, wenn sie in Services gehoert.
- Halte Abhaengigkeiten gerichtet: Router -> Services -> Models.
- Aendere DB-Schema nur mit Alembic-Migrationen.
- Frontend:
  - Views orchestrieren, Komponenten kapseln Darstellung/Interaktion.
  - State in Pinia-Stores, API-Aufrufe zentral und nachvollziehbar.

## Qualitaets-Gates

- Python muss `ruff check` bestehen.
- Frontend muss `npm run lint` und `npm run build` bestehen.
- Fuer Backend-Aenderungen: `pytest` in `backend/tests`.

## Aenderungsprinzipien

- Minimal-invasive Aenderungen mit klarer Begruendung.
- Bei Unsicherheit zuerst Annahmen offenlegen statt stillschweigend Verhalten zu aendern.
- Breaking Changes nur mit expliziter Kennzeichnung und Migrationshinweis.
