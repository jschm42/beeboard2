#!/bin/bash
# ==============================================================================
# 🐝 BeeBoard 2 — Setup Script
# ==============================================================================
# Dieses Skript richtet die virtuelle Umgebung (.venv) für das Backend ein,
# installiert alle Abhängigkeiten und konfiguriert die .env-Datei.
# ==============================================================================

# Farben für Terminal-Ausgabe definieren
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verzeichnisse ermitteln
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/backend"

echo -e "${BLUE}====================================================================${NC}"
echo -e "${BLUE}🐝 BeeBoard 2 — Automatisches Setup & Konfiguration${NC}"
echo -e "${BLUE}====================================================================${NC}\n"

# 1. Python-Installation überprüfen
echo -e "🔎 ${BLUE}Schritt 1: Python-Installation überprüfen...${NC}"
PYTHON_CMD=""

if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
elif command -v py &>/dev/null; then
    PYTHON_CMD="py"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Fehler: Python wurde nicht gefunden!${NC}"
    echo "Bitte installieren Sie Python 3.12+ (Python 3.13 empfohlen) von https://www.python.org/ und versuchen Sie es erneut."
    exit 1
fi

PY_VERSION=$("$PYTHON_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "✅ Python gefunden: ${GREEN}$($PYTHON_CMD --version | head -n 1)${NC} (Kommando: ${GREEN}${PYTHON_CMD}${NC})\n"

# 2. Virtuelle Umgebung (.venv) anlegen
echo -e "🐍 ${BLUE}Schritt 2: Virtuelle Umgebung (.venv) erstellen...${NC}"
if [ -d "$BACKEND_DIR/.venv" ]; then
    echo -e "ℹ️ Eine virtuelle Umgebung existiert bereits unter ${YELLOW}backend/.venv${NC}."
    read -p "Möchten Sie diese löschen und neu erstellen? (y/N): " RECREATE_VENV
    if [[ "$RECREATE_VENV" =~ ^[Yy]$ ]]; then
        echo "Lösche alte Umgebung..."
        rm -rf "$BACKEND_DIR/.venv"
        "$PYTHON_CMD" -m venv "$BACKEND_DIR/.venv"
        echo -e "✅ Neue virtuelle Umgebung erstellt."
    else
        echo "Bestehende Umgebung wird beibehalten."
    fi
else
    "$PYTHON_CMD" -m venv "$BACKEND_DIR/.venv"
    echo -e "✅ Virtuelle Umgebung erstellt unter ${GREEN}backend/.venv${NC}."
fi
echo ""

# 3. Virtuelle Umgebung aktivieren & Abhängigkeiten installieren
echo -e "📦 ${BLUE}Schritt 3: Abhängigkeiten installieren...${NC}"
# Prüfen, wo das Aktivierungsskript liegt (Windows Git Bash vs macOS/Linux)
ACTIVATE_SCRIPT=""
if [ -f "$BACKEND_DIR/.venv/Scripts/activate" ]; then
    ACTIVATE_SCRIPT="$BACKEND_DIR/.venv/Scripts/activate"
elif [ -f "$BACKEND_DIR/.venv/bin/activate" ]; then
    ACTIVATE_SCRIPT="$BACKEND_DIR/.venv/bin/activate"
fi

if [ -n "$ACTIVATE_SCRIPT" ]; then
    echo -e "Aktivierung der virtuellen Umgebung..."
    source "$ACTIVATE_SCRIPT"
    
    echo "Aktualisiere pip..."
    python -m pip install --upgrade pip
    
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        echo "Installiere Pakete aus requirements.txt..."
        pip install -r "$BACKEND_DIR/requirements.txt"
        echo -e "✅ Abhängigkeiten erfolgreich installiert."
    else
        echo -e "${RED}⚠️ requirements.txt nicht in backend/ gefunden!${NC}"
    fi
else
    echo -e "${RED}❌ Aktivierungsskript für .venv nicht gefunden!${NC}"
    exit 1
fi
echo ""

# 4. .env Datei anlegen und konfigurieren
echo -e "🔑 ${BLUE}Schritt 4: Umgebungsvariablen konfigurieren...${NC}"
GENERATE_KEY=true

ENV_PATH="$ROOT_DIR/.env"
ENV_EXAMPLE_PATH="$ROOT_DIR/.env.example"

if [ -f "$ENV_PATH" ]; then
    echo -e "ℹ️ Eine ${YELLOW}.env${NC} Datei existiert bereits im Hauptverzeichnis."
    read -p "Möchten Sie diese mit der .env.example überschreiben? (y/N): " OVERWRITE_ENV
    if [[ "$OVERWRITE_ENV" =~ ^[Yy]$ ]]; then
        cp "$ENV_EXAMPLE_PATH" "$ENV_PATH"
        GENERATE_KEY=true
    else
        echo "Bestehende .env Datei wird beibehalten."
        GENERATE_KEY=false
    fi
else
    cp "$ENV_EXAMPLE_PATH" "$ENV_PATH"
    echo "✅ .env.example wurde nach .env kopiert."
    GENERATE_KEY=true
fi

if [ "$GENERATE_KEY" = true ]; then
    echo "Generiere sicheren SECRET_KEY..."
    RANDOM_SECRET=$("$PYTHON_CMD" -c "import secrets; print(secrets.token_hex(32))")
    
    # Plattformunabhängige Ersetzung mit Python
    "$PYTHON_CMD" -c "
import os
env_path = '$ENV_PATH'
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('SECRET_KEY=\"supersecretkeychangeinproduction1234567890\"', f'SECRET_KEY=\"$RANDOM_SECRET\"')
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)
"
    echo -e "✅ Zufälliger SECRET_KEY wurde in ${GREEN}.env${NC} eingetragen."
fi

# Abfrage des Gemini API Keys
if [ "$GENERATE_KEY" = true ] || [ ! -f "$ENV_PATH" ] || grep -q 'GEMINI_API_KEY=""' "$ENV_PATH" 2>/dev/null; then
    echo -e "\n🤖 ${BLUE}KI-Integration einrichten:${NC}"
    echo "Wenn Sie die KI-Features und den Stockkarten-Entwurf nutzen möchten,"
    echo "können Sie hier Ihren Google Gemini API Key eingeben."
    echo "Diesen erhalten Sie kostenlos unter: https://aistudio.google.com/"
    read -p "Gemini API Key eingeben (oder [Enter] zum Überspringen): " GEMINI_KEY
    
    if [ -n "$GEMINI_KEY" ]; then
        "$PYTHON_CMD" -c "
import os
env_path = '$ENV_PATH'
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('GEMINI_API_KEY=\"\"', f'GEMINI_API_KEY=\"$GEMINI_KEY\"')
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)
"
        echo -e "✅ GEMINI_API_KEY wurde in ${GREEN}.env${NC} gespeichert."
    else
        echo -e "ℹ️ Übersprungen. Sie können den GEMINI_API_KEY später manuell in ${YELLOW}.env${NC} eintragen."
    fi
fi
echo ""

# Ports auslesen fuer die Anleitung am Ende
BACKEND_PORT=$("$PYTHON_CMD" -c "
import os
env_path = '$ENV_PATH'
port = 8000
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('BEEBOARD_BACKEND_PORT='):
                port = line.split('=')[1].strip().strip('\"').strip(\"'\")
                break
print(port)
")

# 5. Abschluss und Anleitung
echo -e "${GREEN}====================================================================${NC}"
echo -e "${GREEN}🎉 Setup erfolgreich abgeschlossen!${NC}"
echo -e "${GREEN}====================================================================${NC}\n"
echo "Gehen Sie wie folgt vor, um BeeBoard 2 zu starten:"
echo ""
echo -e "1. ${BLUE}Backend-Datenbank initialisieren & starten:${NC}"
echo "   cd backend"
echo -e "   # Virtuelle Umgebung aktivieren:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   source .venv/Scripts/activate"
else
    echo "   source .venv/bin/activate"
fi
echo "   # Datenbank mit Standard-Daten befüllen:"
echo "   python -m app.scripts.seed"
echo "   # Server starten:"
echo "   uvicorn app.main:app --reload --port $BACKEND_PORT"
echo ""
echo -e "2. ${BLUE}Frontend installieren & starten:${NC}"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo ""
echo -e "Viel Spaß mit BeeBoard 2! 🐝"
