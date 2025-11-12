# 🚀 Installazione Rapida

## 📥 Passo 0: Scarica il Progetto

### Su un nuovo PC/Server:

**Opzione A - Con Git (consigliato):**
```bash
git clone https://github.com/Attilio81/GoogleFileSearch.git
cd GoogleFileSearch
```

**Opzione B - Download ZIP:**
1. Vai su https://github.com/Attilio81/GoogleFileSearch
2. Click su **Code** → **Download ZIP**
3. Estrai lo ZIP in una cartella
4. Apri il terminale nella cartella estratta

---

## Installazione Automatica (Windows)

### 1. Doppio click su `setup.bat`
Lo script installerà automaticamente:
- ✅ Ambiente virtuale Python
- ✅ Tutte le dipendenze
- ✅ Configurazione iniziale
- ✅ File Search Store (opzionale)

### 2. Configura il file `.env`
Durante l'installazione si aprirà automaticamente. Inserisci:
```env
GEMINI_API_KEY=la-tua-api-key
FILE_SEARCH_STORE_NAME=fileSearchStores/il-tuo-store-id
```

### 3. Avvia l'applicazione
Doppio click su `start.bat`

**Fatto!** L'applicazione sarà disponibile su http://localhost:5000

---

## Installazione Manuale

Se preferisci fare tutto a mano:

```bash
# 1. Crea ambiente virtuale
python -m venv venv

# 2. Attiva ambiente virtuale
.\venv\Scripts\Activate.ps1  # PowerShell
# oppure
.\venv\Scripts\activate.bat  # CMD

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Crea file .env
copy .env.example .env
# Modifica .env con le tue credenziali

# 5. Crea File Search Store (prima volta)
cd backend
python create_store.py
cd ..

# 6. Avvia applicazione
cd backend
python app.py
```

---

## Installazione su Server Linux

### Installazione Automatica

```bash
# 1. Clona repository
git clone https://github.com/Attilio81/GoogleFileSearch.git
cd GoogleFileSearch

# 2. Rendi eseguibili gli script
chmod +x setup.sh start.sh start-production.sh

# 3. Esegui setup
./setup.sh

# 4. Configura .env
nano .env  # Modifica con le tue credenziali

# 5. Avvia applicazione
./start.sh  # Sviluppo
# oppure
./start-production.sh  # Produzione con Gunicorn
```

### Installazione Manuale

```bash
# 1. Clona repository
git clone https://github.com/Attilio81/GoogleFileSearch.git
cd GoogleFileSearch

# 2. Crea ambiente virtuale
python3 -m venv venv
source venv/bin/activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura .env
cp .env.example .env
nano .env  # Modifica con le tue credenziali

# 5. Crea store (prima volta)
cd backend
python3 create_store.py
cd ..

# 6. Avvia
# Sviluppo:
cd backend
python3 app.py

# Produzione con Gunicorn:
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

---

## Ottieni le Credenziali

### API Key Gemini
1. Vai su https://makersuite.google.com/app/apikey
2. Crea una nuova API key
3. Copiala nel file `.env`

### File Search Store
- Durante il `setup.bat` puoi crearlo automaticamente
- Oppure esegui manualmente: `python backend\create_store.py`
- Lo script ti mostrerà il nome dello store da copiare nel `.env`

---

## Risoluzione Problemi

### "Python non trovato"
Installa Python 3.8+ da https://www.python.org/downloads/

### "GEMINI_API_KEY non configurata"
Verifica che il file `.env` contenga la tua API key valida

### "Porta 5000 già in uso"
Modifica la porta in `backend/app.py` (ultima riga)

### Altro?
Consulta `TROUBLESHOOTING.md` per problemi dettagliati

---

## 📱 Interfacce Disponibili

Dopo l'avvio:
- **Admin**: http://localhost:5000 (gestione documenti)
- **Chat**: http://localhost:5000/chat (chatbot)
- **Chunks**: http://localhost:5000/chunks (visualizza chunks)

---

## 🔄 Aggiornamento

```bash
git pull
pip install -r requirements.txt --upgrade
```

Poi riavvia con `start.bat` o `python backend/app.py`
