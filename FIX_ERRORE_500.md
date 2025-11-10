# ✅ RISOLUZIONE ERRORE 500

## Problema Identificato

L'errore 500 era causato da un parametro `pageSize` non valido nelle richieste all'API Google File Search.

### Errore Specifico:
```json
{
  "error": {
    "code": 400,
    "message": "* ListDocumentsRequest.page_size: page_size must be between 1 and 20.\n",
    "status": "INVALID_ARGUMENT"
  }
}
```

## Soluzione Applicata

Ho modificato `backend/app.py` nella funzione `list_documents()`:

**Prima (errato):**
```python
page_size = request.args.get('pageSize', 100)  # ❌ 100 supera il limite di 20
```

**Dopo (corretto):**
```python
page_size = min(int(request.args.get('pageSize', 20)), 20)  # ✅ Max 20 come richiesto da Google
```

## Limitazioni API Documentate

Dalla documentazione ufficiale Google:
- **pageSize max**: 20 documenti per pagina
- **pageSize default**: 10 se non specificato
- **Paginazione**: Usare `nextPageToken` per recuperare più pagine

## Come Avviare il Server

### Metodo 1: PowerShell (Raccomandato per Windows)

```powershell
cd "c:\Progetti Pilota\Gestione Documenti GoogleSearch\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py"
```

### Metodo 2: Batch File

```cmd
cd backend
start_server.bat
```

### Metodo 3: PowerShell Diretto

```powershell
cd backend
python app.py
```

**Nota**: Con il metodo 3, tieni la finestra PowerShell aperta.

## Verifica che Funzioni

```powershell
# Test endpoint documents
Invoke-RestMethod -Uri "http://localhost:5000/api/documents"

# Output atteso:
# {
#   "success": true,
#   "documents": [],
#   "nextPageToken": ""
# }
```

## Altri Parametri Corretti dalla Documentazione

### Upload Documents
- `displayName`: Max 512 caratteri
- `file`: Max 100MB (configurabile in app.py)

### Delete Documents  
- `force=true`: **Obbligatorio** per eliminare anche i chunk

### Stati Documenti
- `STATE_PENDING`: Elaborazione in corso
- `STATE_ACTIVE`: Pronto per ricerca
- `STATE_FAILED`: Errore elaborazione

## Prossimi Passi

1. ✅ Server funzionante su http://localhost:5000
2. ✅ API documents corretta
3. 📤 Prova a caricare un documento
4. 📋 Verifica che appaia nella lista
5. 🔍 Testa la query RAG (se implementata)

---

**Data risoluzione:** 10 Novembre 2025
**Issue:** Errore 500 su /api/documents  
**Root cause:** pageSize=100 eccede limite API Google (max 20)
**Fix:** Limitato pageSize a max 20
