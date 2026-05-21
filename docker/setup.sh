#!/bin/bash
set -e

# Verzeichnis dieses Skripts ermitteln
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

# Fallback auf Werte aus backend/.env
HTTP_PORT=""
HTTPS_PORT=""
BACKEND_PORT=""
DATA_DIR=""

ENV_PATH="$PARENT_DIR/backend/.env"
if [ -f "$ENV_PATH" ]; then
    # Werte einlesen (Kommentare und Leerzeilen ignorieren)
    while IFS='=' read -r key value || [ -n "$key" ]; do
        key=$(echo "$key" | xargs)
        if [[ -n "$key" && ! "$key" =~ ^# ]]; then
            # Anfuehrungszeichen entfernen
            value=$(echo "$value" | tr -d '"' | tr -d "'" | xargs)
            case "$key" in
                BEEBOARD_HTTP_PORT) HTTP_PORT="$value" ;;
                BEEBOARD_HTTPS_PORT) HTTPS_PORT="$value" ;;
                BEEBOARD_BACKEND_PORT) BACKEND_PORT="$value" ;;
                BEEBOARD_DOCKER_DATA) DATA_DIR="$value" ;;
            esac
        fi
    done < "$ENV_PATH"
fi

# Standardwerte setzen falls nicht in .env definiert
: ${HTTP_PORT:=8080}
: ${HTTPS_PORT:=8443}
: ${BACKEND_PORT:=8000}
: ${DATA_DIR:=~/.beeboard2}

# Expand ~ to $HOME
if [[ "$DATA_DIR" =~ ^~ ]]; then
    DATA_DIR="${DATA_DIR/#\~/$HOME}"
fi

# Ensure the directory exists on the host with correct permissions
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
echo -e "\033[1;36mStarte BeeBoard2 Unified Docker Stack mit:\033[0m"
echo -e "\033[1;36m  HTTP Port:        $HTTP_PORT\033[0m"
echo -e "\033[1;36m  HTTPS Port:       $HTTPS_PORT\033[0m"
echo -e "\033[1;36m  Datenverzeichnis: $DATA_DIR\033[0m"
echo ""
echo -e "\033[1;32mSSL-Zertifikate werden bei Bedarf automatisch im Container generiert und in 'docker/certs/' gespeichert.\033[0m"
echo ""

cd "$SCRIPT_DIR"
docker compose -f ./docker-compose.yml up -d --build
