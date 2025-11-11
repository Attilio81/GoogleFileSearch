#!/bin/bash
# ========================================
# Script di Installazione Automatica
# Google File Search Application - Linux
# ========================================

echo ""
echo "===================================="
echo " INSTALLAZIONE GOOGLE FILE SEARCH"
echo "===================================="
echo ""

# Verifica Python
echo "[1/5] Verifica Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERRORE: Python3 non trovato!"
    echo "Installa Python 3.8+ con: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
python3 --version
echo ""

# Crea ambiente virtuale
echo "[2/5] Creazione ambiente virtuale..."
if [ -d "venv" ]; then
    echo "Ambiente virtuale già esistente, lo rimuovo..."
    rm -rf venv
fi
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERRORE: Impossibile creare l'ambiente virtuale"
    exit 1
fi
echo "Ambiente virtuale creato con successo!"
echo ""

# Attiva ambiente virtuale
echo "[3/5] Attivazione ambiente virtuale..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERRORE: Impossibile attivare l'ambiente virtuale"
    exit 1
fi
echo ""

# Installa dipendenze
echo "[4/5] Installazione dipendenze..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRORE: Installazione dipendenze fallita"
    exit 1
fi
echo ""

# Verifica file .env
echo "[5/5] Verifica configurazione..."
if [ ! -f ".env" ]; then
    echo ""
    echo "ATTENZIONE: File .env non trovato!"
    echo ""
    if [ -f ".env.example" ]; then
        echo "Copio .env.example in .env..."
        cp .env.example .env
        echo ""
        echo "IMPORTANTE: Modifica il file .env con le tue credenziali:"
        echo "- GEMINI_API_KEY=la-tua-api-key"
        echo "- FILE_SEARCH_STORE_NAME=il-tuo-store-name"
        echo ""
        echo "Apri .env con: nano .env"
    else
        echo "Creo file .env di esempio..."
        cat > .env << EOF
# Configurazione Google File Search
GEMINI_API_KEY=your-api-key-here
FILE_SEARCH_STORE_NAME=fileSearchStores/your-store-id
DEFAULT_MODEL=gemini-2.5-pro
CHUNK_SIZE=512
CHUNK_OVERLAP_PERCENT=10
EOF
        echo ""
        echo "File .env creato. Aprilo e inserisci le tue credenziali."
        echo "Usa: nano .env"
    fi
else
    echo "File .env trovato!"
fi
echo ""

# Crea store (opzionale)
echo ""
read -p "Vuoi creare un nuovo File Search Store? (s/n): " create_store
if [ "$create_store" = "s" ] || [ "$create_store" = "S" ]; then
    echo ""
    echo "Creazione File Search Store..."
    cd backend
    python3 create_store.py
    cd ..
else
    echo "Store non creato. Puoi crearlo in seguito con: python3 backend/create_store.py"
fi
echo ""

echo "===================================="
echo " INSTALLAZIONE COMPLETATA!"
echo "===================================="
echo ""
echo "Per avviare l'applicazione usa: ./start.sh"
echo ""

# Rendi eseguibile lo script di avvio
chmod +x start.sh 2>/dev/null
