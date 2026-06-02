#!/bin/sh
set -e

# Verzeichnis dieses Skripts ermitteln (POSIX-kompatibel, kein BASH_SOURCE)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Fallback auf Werte aus .env
HTTP_PORT=""
HTTPS_PORT=""
BACKEND_PORT=""
DATA_DIR=""

ENV_PATH="$PARENT_DIR/.env"
if [ ! -f "$ENV_PATH" ]; then
    ENV_PATH="$PARENT_DIR/backend/.env"
fi
if [ -f "$ENV_PATH" ]; then
    # Werte einlesen (Kommentare und Leerzeilen ignorieren)
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Fuehrende/nachfolgende Leerzeichen entfernen
        key=$(echo "$key" | tr -d ' ')
        # Kommentare und Leerzeilen ueberspringen
        case "$key" in
            "#"*|"") continue ;;
        esac
        # Anfuehrungszeichen entfernen
        value=$(echo "$value" | tr -d '"' | tr -d "'")
        case "$key" in
            BEEBOARD_HTTP_PORT)    HTTP_PORT="$value" ;;
            BEEBOARD_HTTPS_PORT)   HTTPS_PORT="$value" ;;
            BEEBOARD_BACKEND_PORT) BACKEND_PORT="$value" ;;
            BEEBOARD_DOCKER_DATA)  DATA_DIR="$value" ;;
        esac
    done < "$ENV_PATH"
fi

# Standardwerte setzen falls nicht in .env definiert
: "${HTTP_PORT:=8080}"
: "${HTTPS_PORT:=8443}"
: "${BACKEND_PORT:=8000}"
: "${DATA_DIR:=$HOME/.beeboard2}"

# Expand ~ to $HOME (POSIX-kompatibel)
case "$DATA_DIR" in
    "~"*) DATA_DIR="$HOME${DATA_DIR#~}" ;;
esac

# Ensure the directory exists on the host
mkdir -p "$DATA_DIR"

# Resolve to absolute path
DATA_DIR="$(cd "$DATA_DIR" && pwd)"

export BEEBOARD_HTTP_PORT="$HTTP_PORT"
export BEEBOARD_HTTPS_PORT="$HTTPS_PORT"
export BEEBOARD_BACKEND_PORT="$BACKEND_PORT"
export BEEBOARD_DOCKER_DATA="$DATA_DIR"

# Sicherstellen, dass das certs-Verzeichnis existiert
mkdir -p "$SCRIPT_DIR/certs"

echo ""
printf "\033[1;36mAktualisiere BeeBoard2 Unified Docker Stack (Rebuild + Restart)...\033[0m\n"
echo ""

echo "Updating repository from git..."
git -C "$PARENT_DIR" pull || echo "Warning: git pull failed, building with current local files."

cd "$SCRIPT_DIR"
docker compose -f ./docker-compose.yml pull
docker compose -f ./docker-compose.yml up -d --build
