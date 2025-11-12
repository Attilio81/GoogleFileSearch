# Documentazione

Questa cartella contiene tutta la documentazione tecnica e guide del progetto.

## Guide Tecniche

### Architettura RAG
- **`LOGICA_FILTRAGGIO_CHUNKS.md`** - Spiega l'architettura RAG a due fasi (Retrieval → Generation) e il sistema di filtraggio chunk per rilevanza

### Troubleshooting
- **`TROUBLESHOOTING.md`** - Guida risoluzione problemi comuni
- **`FIX_ERRORE_500.md`** - Fix errore 500 su generateContent
- **`FIX_ERRORE_UPLOAD.md`** - Fix problemi upload documenti

### Log Modifiche
- **`IMPROVEMENTS_LOG.md`** - Storia miglioramenti e feature aggiunte
- **`CLAUDE.md`** - Note e conversazioni sviluppo con Claude

## Struttura Documentazione

```
docs/
├── README.md                           # Questo file
├── LOGICA_FILTRAGGIO_CHUNKS.md       # Architettura RAG
├── TROUBLESHOOTING.md                 # Risoluzione problemi
├── FIX_ERRORE_500.md                  # Fix specifici
├── FIX_ERRORE_UPLOAD.md              # Fix upload
├── IMPROVEMENTS_LOG.md                # Changelog tecnico
└── CLAUDE.md                          # Note sviluppo
```

## Collegamenti Rapidi

- **README principale**: `../README.md`
- **Setup e Installazione**: `../setup/README.md`
- **Test Suite**: `../backend/tests/README.md`

## Argomenti Principali

### RAG (Retrieval Augmented Generation)
1. **Retrieval Phase**: Query sui documenti → recupero chunks rilevanti
2. **Filtering Phase**: Filtraggio per MIN_RELEVANCE_SCORE
3. **Generation Phase**: Gemini genera risposta basata sui chunk filtrati

### Configurazione
Tutti i parametri configurabili sono in `.env`:
- `MIN_RELEVANCE_SCORE`: Soglia rilevanza (0.0-1.0)
- `MAX_CHUNKS_FOR_GENERATION`: Limite chunks inviati a Gemini
- `RESULTS_COUNT`: Chunks recuperati da API
- `CHUNK_SIZE`: Dimensione chunk (1-512 token)

### Performance
- **Cache**: Query cache con TTL (default: 5 minuti)
- **Rate Limiting**: 30 richieste/minuto per IP
- **Connection Pooling**: Session pooling per API calls

Vedi singoli file per dettagli specifici.
