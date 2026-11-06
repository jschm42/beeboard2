---
description: Pflicht-Sicherheitsregeln fuer BeeBoard 2 - Secrets, Eingabevalidierung, Authentifizierung/Autorisierung, SQL-Injection, Logging und sichere Defaults.
trigger: model_decision
---

# Security

1. **Secrets**: Niemals Secrets, Tokens, API-Keys oder personenbezogene Daten hardcoden. Werte kommen aus
   Umgebungsvariablen ueber `backend/app/core/config.py` (`.env`, Vorlage `.env.example`).
2. **Eingabevalidierung**: Alle API-Eingaben ueber Pydantic-Schemas plus defensive Checks validieren.
3. **AuthN/AuthZ**:
   * Geschuetzte Endpunkte verlangen `current_user: User = Depends(get_current_user)` (`app.core.security`).
   * Zugriff auf Bienenstaende, Voelker und abhaengige Daten nur ueber die Mitgliedschaft
     (`ApiaryMembership`) des aktuellen Benutzers; fremde Ressourcen mit 404/403 beantworten.
   * Der MCP-Server authentifiziert ueber `BEEBOARD_API_KEY` (gehasht in `ApiKey`).
4. **SQL-Injection**: Nur SQLAlchemy ORM/Core mit parametrisierten Queries.
5. **Logging**: Keine sensiblen Daten loggen (Passwoerter, Tokens, API-Keys, persoenliche Inhalte).
6. **Datei-Uploads**: Dateinamen nie ungeprueft fuer Pfade verwenden; zufaellige UUID-Namen bzw.
   `os.path.basename` nutzen und im Upload-Verzeichnis bleiben.
7. **Sichere Defaults**: deny by default, least privilege, fail closed.
