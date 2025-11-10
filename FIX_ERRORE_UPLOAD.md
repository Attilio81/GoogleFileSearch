# ✅ RISOLUZIONE ERRORE 500 - UPLOAD

## Problema Identificato

L'errore 500 sull'endpoint `/api/documents/upload` era causato da un formato errato della richiesta multipart.

### Errore Specifico dall'API Google:
```
Payload parts count different from expected 2. Request payload parts count: 3
```

## Causa Root

L'API Google File Search `uploadToFileSearchStore` richiede **esattamente 2 parti** nel multipart upload:
1. **metadata** (JSON)
2. **file** (contenuto binario)

Il codice precedente inviava 3 parti perché utilizzava sia `files` che `data` in `requests.post()`.

## Soluzione Applicata

### Prima (errato):
```python
# Metadati nel dizionario sbagliato
metadata = {
    'document': {  # ❌ Struttura errata
        'displayName': display_name,
        'mimeType': mime_type
    }
}

files = {
    'metadata': (None, str(metadata).replace("'", '"'), 'application/json'),  # ❌ Conversione manuale
    'file': (filename, file.stream, mime_type)
}

# data parametro creava una terza parte ❌
response = requests.post(url, headers=headers, files=files, data=other_data)
```

### Dopo (corretto):
```python
import json

# Metadati nel formato corretto (senza 'document' wrapper)
metadata = {
    'displayName': display_name[:512],
    'mimeType': mime_type
}

if custom_metadata:
    metadata['customMetadata'] = [
        {'key': k, 'stringValue': v} for k, v in custom_metadata.items()
    ]

# Solo 2 parti nel multipart ✅
files = {
    'metadata': (None, json.dumps(metadata), 'application/json'),  # ✅ JSON corretto
    'file': (secure_filename(file.filename), file.stream, mime_type)
}

# NO data parameter ✅
response = requests.post(url, headers=headers, files=files)
```

## Test Eseguito

```bash
python backend/test_upload.py

# Risultato:
✅ Status Code: 200
✅ Upload avviato con successo!
✅ Documento creato: test-document-upload-xxx
✅ Stato: STATE_ACTIVE
```

## Formato Corretto API Google

Secondo la documentazione ufficiale:

**Endpoint:**
```
POST https://generativelanguage.googleapis.com/upload/v1beta/{fileSearchStoreName}:uploadToFileSearchStore
```

**Multipart Payload (esattamente 2 parti):**

1. **metadata** (application/json):
```json
{
  "displayName": "Nome documento",
  "mimeType": "text/plain",
  "customMetadata": [
    {"key": "chiave", "stringValue": "valore"}
  ],
  "chunkingConfig": { ... }  // opzionale
}
```

2. **file** (contenuto):
- File binario con il MIME type appropriato

## Verifica Funzionamento

1. **Server attivo:** http://localhost:5000
2. **Upload funzionante:** ✅
3. **Documento creato:** ✅ `test-document-upload-xxx`
4. **Stato:** `STATE_ACTIVE` (pronto per query)

## Limitazioni e Note

- **displayName**: Max 512 caratteri
- **File size**: Max 100MB (configurabile in `app.config['MAX_CONTENT_LENGTH']`)
- **Response**: Restituisce un `Operation` object per il tracking asincrono
- **Stati possibili**:
  - `STATE_PENDING`: Elaborazione in corso
  - `STATE_ACTIVE`: Pronto per ricerca
  - `STATE_FAILED`: Errore elaborazione

## File Modificati

- ✅ `backend/app.py` - Funzione `upload_document()`
- ✅ `backend/test_upload.py` - Script di test

## Prossimi Passi

1. ✅ Upload funzionante
2. ✅ Documenti visualizzati nella lista
3. 📤 Testa upload dalla UI web
4. 🗑️ Testa eliminazione documenti
5. 🔍 Implementa query RAG (se necessario)

---

**Data risoluzione:** 10 Novembre 2025  
**Issue:** Errore 500 su /api/documents/upload  
**Root cause:** Multipart payload con 3 parti invece di 2  
**Fix:** Rimossa struttura 'document' e parametro 'data'  
**Status:** ✅ RISOLTO E TESTATO
