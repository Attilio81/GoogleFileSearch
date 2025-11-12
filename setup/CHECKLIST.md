# ✅ Checklist Installazione Nuovo PC/Server

## Prima di Iniziare

- [ ] Python 3.8 o superiore installato
- [ ] Git installato (opzionale ma consigliato)
- [ ] Accesso internet attivo
- [ ] API Key Gemini disponibile → [Ottieni qui](https://makersuite.google.com/app/apikey)

---

## 📥 Installazione Windows

### Passo 1: Scarica il Progetto
- [ ] Scarica da GitHub:
  ```bash
  git clone https://github.com/Attilio81/GoogleFileSearch.git
  cd GoogleFileSearch
  ```
  **oppure** scarica ZIP e estrai

### Passo 2: Setup Automatico
- [ ] Doppio click su `setup.bat`
- [ ] Attendi completamento installazione

### Passo 3: Configurazione
- [ ] Si apre automaticamente il file `.env`
- [ ] Inserisci `GEMINI_API_KEY=la-tua-api-key`
- [ ] Durante setup scegli `s` per creare il File Search Store
- [ ] Copia il `FILE_SEARCH_STORE_NAME` nel `.env`
- [ ] Salva e chiudi `.env`

### Passo 4: Avvio
- [ ] Doppio click su `start.bat`
- [ ] Apri browser su http://localhost:5000
- [ ] Testa upload di un documento
- [ ] Testa chat su http://localhost:5000/chat

---

## 🐧 Installazione Linux/Server

### Passo 1: Scarica il Progetto
- [ ] Clona repository:
  ```bash
  git clone https://github.com/Attilio81/GoogleFileSearch.git
  cd GoogleFileSearch
  ```

### Passo 2: Setup Automatico
- [ ] Rendi eseguibili gli script:
  ```bash
  chmod +x setup.sh start.sh start-production.sh
  ```
- [ ] Esegui setup:
  ```bash
  ./setup.sh
  ```

### Passo 3: Configurazione
- [ ] Modifica `.env`:
  ```bash
  nano .env
  ```
- [ ] Inserisci `GEMINI_API_KEY` e `FILE_SEARCH_STORE_NAME`
- [ ] Salva (CTRL+O, ENTER) ed esci (CTRL+X)

### Passo 4: Avvio

**Sviluppo/Test:**
- [ ] `./start.sh`

**Produzione:**
- [ ] `./start-production.sh`
- [ ] Configura firewall per porta 5000:
  ```bash
  sudo ufw allow 5000
  ```

### Passo 5: Test
- [ ] Apri browser su http://server-ip:5000
- [ ] Testa funzionalità

---

## 🔧 Configurazione Opzionale

### Personalizza Parametri
Nel file `.env` puoi modificare:
- [ ] `DEFAULT_MODEL` - Modello Gemini (gemini-2.5-pro, gemini-2.5-flash)
- [ ] `CHUNK_SIZE` - Dimensione chunk (1-512, default 512)
- [ ] `CHUNK_OVERLAP_PERCENT` - Sovrapposizione chunk (0-100, default 10)

### Cambia Porta
Nel file `backend/app.py` ultima riga:
- [ ] Modifica `port=5000` con altra porta

---

## 🚨 Troubleshooting

### "Python non trovato"
- [ ] Installa Python da https://www.python.org/downloads/
- [ ] Durante installazione, seleziona "Add Python to PATH"

### "GEMINI_API_KEY non configurata"
- [ ] Verifica che `.env` esista
- [ ] Verifica che contenga `GEMINI_API_KEY=...` con valore valido
- [ ] Nessuno spazio prima/dopo `=`

### "Porta 5000 già in uso"
- [ ] Modifica porta in `backend/app.py`
- [ ] Oppure termina processo sulla porta 5000

### Upload fallisce
- [ ] Verifica che `FILE_SEARCH_STORE_NAME` sia corretto
- [ ] File max 100MB
- [ ] Formato file supportato (PDF, TXT, DOC, etc.)

### Altro?
- [ ] Consulta `TROUBLESHOOTING.md`
- [ ] Controlla log in `logs/` (produzione)

---

## ✅ Installazione Completata

Se tutti i test funzionano:
- ✅ Upload documenti funziona
- ✅ Lista documenti visibile
- ✅ Chat risponde correttamente
- ✅ Chunks visualizzati

🎉 **Complimenti! L'applicazione è pronta all'uso!**

---

## 📚 Prossimi Passi

- [ ] Carica i tuoi documenti
- [ ] Configura metadati personalizzati
- [ ] Testa query complesse nella chat
- [ ] Monitora performance e log
- [ ] Configura backup periodici

Per aggiornamenti futuri:
```bash
git pull
pip install -r requirements.txt --upgrade
```
