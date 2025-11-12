#!/bin/bash
# ========================================
# Script di Avvio Rapido
# Google File Search Application - Linux
# ========================================

# Vai alla root del progetto (cartella padre di setup/)
cd "$(dirname "$0")/.."

echo ""
echo "===================================="
echo " AVVIO GOOGLE FILE SEARCH"
echo "===================================="
echo ""

# Verifica ambiente virtuale
if [ ! -d "venv" ]; then
    echo "ERRORE: Ambiente virtuale non trovato!"
    echo "Esegui prima setup/setup.sh per installare l'applicazione."
    exit 1
fi

# Verifica file .env
if [ ! -f ".env" ]; then
    echo "ERRORE: File .env non trovato!"
    echo "Configura il file .env con le tue credenziali."
    exit 1
fi

# Attiva ambiente virtuale
echo "Attivazione ambiente virtuale..."
source venv/bin/activate

# Avvia applicazione
echo ""
echo "Avvio server Flask..."
echo ""
echo "Applicazione disponibile su:"
echo "- Admin Interface: http://localhost:5000"
echo "- Chat Interface:  http://localhost:5000/chat"
echo "- Chunks Viewer:   http://localhost:5000/chunks"
echo ""
echo "Premi CTRL+C per fermare il server"
echo ""
echo "===================================="
echo ""

cd backend
python3 app.py
