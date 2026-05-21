#!/bin/sh
# Exit on error
set -e

# 1. SSL-Zertifikate pruefen & generieren (falls nicht gemountet/vorhanden)
mkdir -p /etc/nginx/certs
if [ ! -f /etc/nginx/certs/nginx.crt ] || [ ! -f /etc/nginx/certs/nginx.key ]; then
    echo "SSL-Zertifikate nicht gefunden. Generiere selbstsignierte SSL-Zertifikate direkt im Container..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/certs/nginx.key \
        -out /etc/nginx/certs/nginx.crt \
        -subj '/CN=localhost'
    echo "[+] SSL-Zertifikate erfolgreich generiert."
else
    echo "[+] Vorhandene SSL-Zertifikate werden verwendet."
fi

# 2. Datenbank-Migrationen & Seeding
echo "Fuehre Datenbank-Migrationen aus..."
alembic upgrade head

echo "Fuehre Datenbank-Seeding aus..."
python -m app.scripts.seed

# 3. Backend (Uvicorn) im Hintergrund auf localhost:8000 starten
echo "Starte FastAPI Backend (Uvicorn)..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# 4. HTTPS-Port in Nginx konfigurieren und Nginx im Vordergrund starten (haelt den Container am Laufen)
echo "Konfiguriere HTTPS-Port in Nginx: ${BEEBOARD_HTTPS_PORT:-8443}"
sed -i "s/__HTTPS_PORT__/${BEEBOARD_HTTPS_PORT:-8443}/g" /etc/nginx/nginx.conf

echo "Starte Nginx Reverse Proxy..."
exec nginx -g "daemon off;"
