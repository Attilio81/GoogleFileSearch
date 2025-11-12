# 🔧 Troubleshooting Guide

## Problemi Comuni e Soluzioni

### 1. ❌ Errore 500 su `/api/documents` e `/api/documents/upload`

**Sintomi:**
- Errore 500 (Internal Server Error) quando si carica la pagina
- Console del browser mostra errori sulle chiamate API
- Nessun documento visualizzato

**Causa Principale:**
Nome del File Search Store non valido o store inesistente.

**Soluzione:**

1. **Crea un nuovo File Search Store:**
   ```powershell
   cd backend
   python create_store.py
   ```

2. **Copia il nome dello store** mostrato nell'output (es: `fileSearchStores/xxx-yyy-zzz`)

3. **Aggiorna il file `.env`:**
   ```env
   FILE_SEARCH_STORE_NAME=fileSearchStores/xxx-yyy-zzz
   ```

4. **Riavvia il server:**
   ```powershell
   # Ferma il server (Ctrl+C)
   python app.py
   ```

### 2. ❌ Errore 404 su `/favicon.ico`

**Sintomi:**
- Errore 404 nella console del browser
- Non influisce sulla funzionalità ma genera warning

**Soluzione:**
Il file `favicon.svg` è già incluso. Se l'errore persiste, pulisci la cache del browser (Ctrl+Shift+Del).

### 3. ❌ `ModuleNotFoundError: No module named 'flask'`

**Sintomi:**
- Il server non si avvia
- Errore durante l'importazione dei moduli

**Soluzione:**
```powershell
# Installa le dipendenze
pip install -r requirements.txt
```

### 4. ❌ Errore 400: "FileSearchStore name must be of the format fileSearchStores/*"

**Sintomi:**
- L'API restituisce errore 400
- Messaggio di formato nome store non valido

**Causa:**
Il nome dello store in `.env` non è corretto o troppo generico (es: `fileSearchStores/MyStore`).

**Soluzione:**
Usa lo script `create_store.py` per creare uno store con un nome valido generato automaticamente da Google.

### 5. ⚠️ Le operazioni di upload restano su "STATE_PENDING" troppo a lungo

**Sintomi:**
- Il documento viene caricato ma rimane "In elaborazione" per molto tempo
- Non diventa mai "STATE_ACTIVE"

**Cause Possibili:**
- File molto grande (elaborazione embeddings richiede tempo)
- Problemi di rete
- Errore nell'elaborazione del documento

**Soluzione:**
1. Controlla i log del server per errori
2. Verifica manualmente lo stato con:
   ```powershell
   python test_api.py
   ```
3. Attendi alcuni minuti per file grandi (>10MB)
4. Se persiste oltre 10 minuti, probabilmente c'è un errore nell'elaborazione

### 6. 🔑 Errore di Autenticazione API

**Sintomi:**
- Errore 401 o 403
- "API key not valid" o "Permission denied"

**Soluzione:**
1. Verifica che la API Key in `.env` sia corretta
2. Controlla che la chiave non sia scaduta su https://makersuite.google.com/app/apikey
3. Assicurati che l'API Gemini sia abilitata nel tuo progetto Google Cloud

### 7. 🌐 CORS Error nel browser

**Sintomi:**
- Errore CORS nella console del browser
- Le richieste vengono bloccate

**Soluzione:**
Il server Flask ha già `flask-cors` installato e configurato. Se il problema persiste:
1. Verifica che il frontend sia servito dallo stesso server (localhost:5000)
2. Non aprire il file HTML direttamente (deve essere servito da Flask)

### 8. 📤 Upload fallisce con file grandi

**Sintomi:**
- Upload si blocca o fallisce
- Timeout durante l'upload

**Soluzione:**
1. Limite corrente: 100MB per file
2. Per aumentare il limite, modifica in `app.py`:
   ```python
   app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB
   ```

### 9. 🗑️ Eliminazione fallisce con "FAILED_PRECONDITION"

**Sintomi:**
- Errore durante eliminazione documento
- Messaggio su chunk presenti

**Soluzione:**
L'applicazione usa automaticamente `force=true`. Se il problema persiste:
1. Verifica che l'endpoint DELETE usi il parametro `force=true`
2. Controlla i log del server per dettagli

## 🔍 Debug Avanzato

### Abilitare Log Dettagliati

Modifica `app.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Cambia da INFO a DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Testare API Direttamente

Usa gli script di utility:

```powershell
# Test connessione
python backend/test_api.py

# Crea nuovo store
python backend/create_store.py
```

### Verificare Configurazione

```powershell
python setup.py
```

## 📞 Supporto

Se il problema persiste:

1. Controlla i log del server (terminale dove gira `python app.py`)
2. Controlla la console del browser (F12 → Console)
3. Verifica lo stato delle API Google su https://status.cloud.google.com/

## ✅ Checklist Pre-Avvio

- [ ] Python 3.8+ installato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] File `.env` creato e configurato
- [ ] API Key valida
- [ ] File Search Store creato
- [ ] Server avviato senza errori

---

**Ultimo aggiornamento:** 10 Novembre 2025
