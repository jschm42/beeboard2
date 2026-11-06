---
name: beeboard-mcp-server
description: BeeBoard-MCP-Server (FastMCP) starten, in MCP-Clients wie Claude Code oder Claude Desktop einbinden, per API-Key authentifizieren und neue MCP-Tools fuer Bienenstaende, Voelker, Logbuch, Honigverkauf, Aufgaben und Behandlungen ergaenzen.
---

# BeeBoard 2 MCP-Server

`backend/app/mcp_server.py` stellt einen FastMCP-Server ("BeeBoard") bereit, ueber den Agents Daten lesen und
schreiben koennen.

---

## 1. Starten (stdio)

```bash
cd backend
BEEBOARD_API_KEY=<key> poetry run python -m app.mcp_server
```

Den API-Key erzeugt der Benutzer in der App unter "API Keys"; gespeichert wird nur der SHA-256-Hash (`ApiKey`). Ohne
`BEEBOARD_API_KEY` faellt der Server fuer die lokale Nutzung auf den ersten aktiven Benutzer zurueck.

## 2. In Claude Code einbinden

```bash
claude mcp add beeboard --env BEEBOARD_API_KEY=<key> -- poetry -C <repo>/backend run python -m app.mcp_server
```

## 3. Vorhandene Tools

`list_apiaries`, `list_hives`, `search_hive_by_name`, `create_journal_note`, `list_sales_products`,
`create_honey_sale`, `list_honey_sales`, `get_hive_inspection_stats`, `list_tasks`, `create_task`,
`list_treatments`, `create_treatment`, `list_treatment_methods`, `list_treatment_application_types`.

## 4. Neues Tool ergaenzen

1. Funktion mit `@mcp.tool()` in `app/mcp_server.py` anlegen, Docstring beschreibt Zweck und Parameter (das sieht
   das LLM).
2. Benutzer ueber `get_user_from_env(db)` aufloesen und Zugriff **immer** ueber `ApiaryMembership` pruefen
   (siehe `.claude/rules/security.md`).
3. Fachlogik aus `app/services/` wiederverwenden statt sie zu duplizieren.
4. Ueber MCP angelegte Logbuch-Eintraege mit `created_via_mcp=True` markieren.
5. Test in `tests/test_mcp_server.py` ergaenzen und `poetry run pytest tests/test_mcp_server.py` ausfuehren.
