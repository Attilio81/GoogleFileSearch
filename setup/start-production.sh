#!/bin/bash
# ========================================
# Script di Avvio per PRODUZIONE
# Google File Search Application - Linux
# ========================================

# Vai alla root del progetto (cartella padre di setup/)
cd "$(dirname "$0")/.."

echo ""
echo "===================================="
echo " AVVIO SERVER PRODUZIONE"
echo "===================================="
echo ""

# Verifica ambiente virtuale
if [ ! -d "venv" ]; then
    echo "ERRORE: Ambiente virtuale non trovato!"
    echo "Esegui prima setup/setup.sh"
    exit 1
fi

# Verifica file .env
if [ ! -f ".env" ]; then
    echo "ERRORE: File .env non trovato!"
    exit 1
fi

# Attiva ambiente virtuale
source venv/bin/activate

# Verifica Gunicorn o Waitress
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn non trovato. Installazione..."
    pip install gunicorn
fi

# Configurazione server
WORKERS=4
HOST="0.0.0.0"
PORT=5000
TIMEOUT=120

echo "Configurazione:"
echo "- Workers: $WORKERS"
echo "- Host: $HOST"
echo "- Port: $PORT"
echo "- Timeout: ${TIMEOUT}s"
echo ""
echo "Applicazione disponibile su:"
echo "- Admin Interface: http://<server-ip>:$PORT"
echo "- Chat Interface:  http://<server-ip>:$PORT/chat"
echo "- Chunks Viewer:   http://<server-ip>:$PORT/chunks"
echo ""
echo "Premi CTRL+C per fermare il server"
echo ""
echo "===================================="
echo ""

# Avvia Gunicorn
cd backend
gunicorn -w $WORKERS \
         -b $HOST:$PORT \
         --timeout $TIMEOUT \
         --access-logfile ../logs/access.log \
         --error-logfile ../logs/error.log \
         --log-level info \
         app:app
