# 🤖 Google File Search RAG - Sistema di Gestione Documenti e Chatbot

Sistema completo per la gestione di documenti e chatbot basato su **Google File Search API** e **Gemini AI**. Implementa un sistema RAG (Retrieval-Augmented Generation) avanzato per interrogare documenti con intelligenza artificiale.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![Google AI](https://img.shields.io/badge/Google%20AI-Gemini-orange)
![RAG](https://img.shields.io/badge/RAG-Optimized-purple)

---

## 🚀 Quick Start (Nuovo PC)

### 1️⃣ Scarica il progetto
```bash
git clone https://github.com/Attilio81/GoogleFileSearch.git
cd GoogleFileSearch
```

### 2️⃣ Installa (Windows)
Doppio click su **`setup/setup.bat`** → Installa tutto automaticamente

### 3️⃣ Configura `.env`
Si apre automaticamente. Inserisci:
```env
GEMINI_API_KEY=la-tua-api-key
FILE_SEARCH_STORE_NAME=fileSearchStores/il-tuo-store-id
```
[Ottieni API Key](https://makersuite.google.com/app/apikey)

### 4️⃣ Avvia
Doppio click su **`setup/start.bat`**

✅ **Fatto!** Vai su http://localhost:5000

📖 Guida completa: [setup/INSTALL.md](setup/INSTALL.md)

---

## 🎯 Funzionalità

### 🗂️ Gestione Documenti

- **📤 Upload Documenti**: Carica file nel File Search Store con gestione asincrona (Long-Running Operations)
- **📋 Visualizzazione**: Lista completa dei documenti con stato, dimensione e metadati
- **🔍 Monitoraggio**: Tracking in tempo reale delle operazioni di upload in corso
- **🗑️ Eliminazione**: Rimozione sicura dei documenti con conferma (elimina anche i chunk associati)
- **⚙️ Metadati Custom**: Supporto per metadati personalizzati durante l'upload con chiave riservata `document_location` per percorsi file
- **✂️ Chunking Configurabile**: Dimensione chunk (1-512 token) e overlap (0-50%) personalizzabili
- **🔗 Fonti Cliccabili**: Apertura diretta dei documenti originali tramite metadato `document_location`
- **📊 Visualizzazione Chunks**: Modal per visualizzare tutti i chunks di ogni documento
- **Formati supportati**: PDF, TXT, DOC, DOCX, XLS, XLSX, CSV, JSON, HTML, MD

### 💬 Chatbot RAG (Ottimizzato)

- **🔍 Retrieval semantico avanzato** con filtro per relevance score
- **🎯 Filtraggio intelligente**: Solo chunks con score >= 0.3 (configurabile)
- **📉 Riduzione rumore**: Massimo 15 chunks più rilevanti inviati a Gemini (configurabile)
- **🤖 Generazione risposte sintetizzate** con prompt engineering ottimizzato
- **💭 Conversazioni multi-turn** con memoria del contesto
- **📚 Visualizzazione fonti pertinenti** solo dai documenti effettivamente utilizzati
- **📄 Apertura documenti**: Click su "Apri Documento" per vedere il file originale
- **⚙️ Selezione modello** Gemini configurabile (gemini-2.5-flash, gemini-2.5-pro)
- **🔄 Circuit Breaker**: Gestione automatica rate limit con fallback
- **📊 Configurazione dinamica**: Numero chunks recuperati (RESULTS_COUNT) configurabile
- **🎛️ Streaming SSE**: Risposte in tempo reale con Server-Sent Events
- **📱 Design responsive** per mobile e desktop

## 🏗️ Architettura

```
User Query → Retrieval (File Search API) → Generation (Gemini) → Response
             ↓ Semantic Search              ↓ Context + Prompt
             Relevant Chunks                 AI-Generated Answer
```

### Struttura Progetto

```
GoogleFileSearch/
├── backend/                      # Backend Flask
│   ├── app.py                    # Flask app principale
│   ├── create_store.py           # Crea File Search Store
│   ├── test_*.py                 # Script di test API
│   └── tests/                    # Test suite (pytest)
│       ├── test_rag.py           # Test validazione RAG
│       └── README.md             # Guida esecuzione test
├── frontend/                     # Frontend HTML/CSS/JS
│   ├── static/
│   │   ├── css/                  # Stili
│   │   └── js/                   # JavaScript
│   └── templates/                # Template HTML
│       ├── index.html            # Admin UI
│       ├── chat.html             # Chat UI
│       └── chunks.html           # Visualizzazione chunks
├── setup/                        # 📁 Script installazione e avvio
│   ├── setup.bat/sh              # Installazione automatica
│   ├── start.bat/sh              # Avvio development
│   ├── start-production.sh       # Avvio production
│   ├── INSTALL.md                # Guida installazione
│   └── CHECKLIST.md              # Checklist setup
├── docs/                         # 📚 Documentazione tecnica
│   ├── LOGICA_FILTRAGGIO_CHUNKS.md  # Architettura RAG
│   ├── TROUBLESHOOTING.md        # Risoluzione problemi
│   ├── IMPROVEMENTS_LOG.md       # Changelog
│   └── README.md                 # Indice documentazione
├── documents_storage/            # Storage documenti caricati
├── logs/                         # Log applicazione
├── venv/                         # Virtual environment Python
├── .env                          # ⚙️ Configurazione (da creare)
├── .env.example                  # Template configurazione
├── requirements.txt              # Dipendenze Python
└── README.md                     # 📖 Questa documentazione
```

## 🚀 Setup e Installazione

### 1. Prerequisiti

- Python 3.8 o superiore
- Account Google Cloud con accesso alle Gemini API
- API Key di Google Gemini ([Ottienila qui](https://makersuite.google.com/app/apikey))
- File Search Store già creato

### 2. Clona il Repository

```bash
git clone https://github.com/Attilio81/GoogleFileSearch.git
cd GoogleFileSearch
```

### 3. Crea Ambiente Virtuale

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 5. Configura Variabili d'Ambiente

Crea un file `.env` copiando `.env.example`:

```bash
cp .env.example .env
```

Modifica `.env` con i tuoi dati:

```env
# API Configuration
GEMINI_API_KEY=la_tua_api_key
FILE_SEARCH_STORE_NAME=fileSearchStores/il-tuo-store-id
DEFAULT_MODEL=gemini-2.5-flash

# Chunking Configuration
CHUNK_SIZE=512                    # Dimensione chunk in token (1-512)
CHUNK_OVERLAP_PERCENT=25          # Overlap tra chunks (0-50%)

# RAG Configuration
RESULTS_COUNT=25                  # Chunks da recuperare (10-40)
MIN_RELEVANCE_SCORE=0.3          # Soglia minima rilevanza (0.0-1.0)
MAX_CHUNKS_FOR_GENERATION=15     # Max chunks per generazione (1-25)
```

#### Come ottenere l'API Key:

1. Vai su https://makersuite.google.com/app/apikey
2. Crea un nuovo progetto o seleziona uno esistente
3. Genera una nuova API Key
4. Copia la chiave nel file `.env`

#### Come creare un File Search Store:

Puoi creare un File Search Store tramite API REST:

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/fileSearchStores" \
  -H "x-goog-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "My RAG Store"
  }'
```

La risposta conterrà il nome della risorsa (es: `fileSearchStores/abc123`) da usare in `.env`.

### 6. Avvia il Server

```bash
cd backend
python app.py
```

Il server sarà disponibile su: **http://localhost:5000**

### 7. Accedi all'Interfaccia

- **Admin Panel:** http://localhost:5000
- **Chatbot:** http://localhost:5000/chat

## 📖 Utilizzo

### Caricamento Documenti

1. Clicca su "Seleziona File" e scegli il documento
2. (Opzionale) Specifica un nome visualizzazione custom
3. (Opzionale) Aggiungi metadati personalizzati
4. Clicca "Carica Documento"
5. L'operazione verrà tracciata nella sezione "Operazioni in Corso"

### Monitoraggio Stato

La tabella mostra tutti i documenti con il loro stato:
- **✅ Attivo**: Documento pronto per la ricerca
- **⏳ In elaborazione**: Upload completato, elaborazione embedding in corso
- **❌ Fallito**: Errore durante l'elaborazione

### Eliminazione Documenti

1. Clicca sul pulsante "🗑️ Elimina" nella riga del documento
2. Conferma l'eliminazione nel modal
3. Il documento e tutti i chunk associati verranno eliminati

### Utilizzo Chatbot

1. Carica documenti tramite Admin Panel
2. Accedi al chatbot (http://localhost:5000/chat)
3. Fai una domanda - Il sistema:
   - Cerca nei documenti i passaggi rilevanti (Retrieval)
   - Genera una risposta contestualizzata (Generation)
   - Mostra le fonti utilizzate

## 🔌 API Endpoints

### Configurazione

- `GET /api/config` - Restituisce la configurazione corrente completa
  - Parametri: chunk_size, chunk_overlap_percent, results_count, min_relevance_score, max_chunks_for_generation

### Gestione Documenti

- `GET /api/documents` - Lista documenti con paginazione
- `POST /api/documents/upload` - Upload documento (Long-Running Operation)
  - Supporta metadati custom e `document_location` per percorso file
- `POST /api/documents/{name}/chunks` - Recupera chunks di un documento
- `DELETE /api/documents/{name}` - Elimina documento (force=true elimina anche chunks)
- `GET /api/operations/{name}` - Stato operazione di upload

### Chatbot RAG

- `POST /api/chat/query` - Retrieval Phase (cerca chunk rilevanti)
  - Parametri: query, results_count (opzionale)
  - Restituisce: relevant_chunks con chunkRelevanceScore
- `POST /api/chat/generate` - Generation Phase (genera risposta)
  - Parametri: query, relevant_chunks, model (opzionale)
  - Applica filtro MIN_RELEVANCE_SCORE e MAX_CHUNKS_FOR_GENERATION
- `POST /api/chat/generate-stream` - Generation con SSE streaming
  - Stessi parametri di generate, ma risposta in streaming

### Interfacce

- `GET /` - Admin panel (gestione documenti)
- `GET /chat` - Chatbot interface (RAG queries)
- `GET /chunks` - Chunks viewer (visualizzazione chunks)

## 🤖 Modelli Gemini Supportati

| Modello | Velocità | Rate Limit | Consigliato |
|---------|----------|------------|-------------|
| `gemini-2.5-flash-lite` | Veloce | Alto | ✅ Default |
| `gemini-1.5-flash-latest` | Veloce | Alto | ✅ Alternativa |
| `gemini-1.5-pro-latest` | Medio | Medio | Per query complesse |
| `gemini-2.0-flash-exp` | Variabile | Basso | ⚠️ Solo test |

## ⚙️ Configurazione Avanzata

### Parametri RAG Ottimizzati

| Parametro | Default | Range | Descrizione |
|-----------|---------|-------|-------------|
| `CHUNK_SIZE` | 512 | 1-512 | Token per chunk (limite API Google) |
| `CHUNK_OVERLAP_PERCENT` | 25% | 0-50% | Sovrapposizione tra chunks per continuità |
| `RESULTS_COUNT` | 25 | 10-100 | Chunks da recuperare dalla ricerca semantica |
| `MIN_RELEVANCE_SCORE` | 0.3 | 0.0-1.0 | Soglia minima per includere chunk nella risposta |
| `MAX_CHUNKS_FOR_GENERATION` | 15 | 1-25 | Max chunks inviati a Gemini per generazione |

### Scenari di Utilizzo

**📄 Documenti Semplici (FAQ, Guide Brevi)**
```env
RESULTS_COUNT=15
MIN_RELEVANCE_SCORE=0.4
MAX_CHUNKS_FOR_GENERATION=10
```

**📚 Documenti Tecnici (Manuali, Preventivi)** ✅ CONSIGLIATO
```env
RESULTS_COUNT=25
MIN_RELEVANCE_SCORE=0.3
MAX_CHUNKS_FOR_GENERATION=15
```

**� Analisi Complesse (Multi-Documento)**
```env
RESULTS_COUNT=40
MIN_RELEVANCE_SCORE=0.2
MAX_CHUNKS_FOR_GENERATION=20
```

### Come Funziona il Filtro Intelligente

1. **Retrieval**: Recupera `RESULTS_COUNT` chunks (es. 25)
2. **Filtro Score**: Scarta chunks con score < `MIN_RELEVANCE_SCORE`
3. **Top-N Selection**: Prende i primi `MAX_CHUNKS_FOR_GENERATION` (es. 15)
4. **Generation**: Invia solo i 15 migliori a Gemini

**Vantaggi**:
- ✅ Riduce "rumore" da chunks non pertinenti
- ✅ Velocizza generazione (meno token)
- ✅ Migliora qualità risposta (contesto più focalizzato)
- ✅ Mostra solo fonti realmente rilevanti

📖 **Dettagli**: Vedi [LOGICA_FILTRAGGIO_CHUNKS.md](LOGICA_FILTRAGGIO_CHUNKS.md)

## �🔧 Troubleshooting

### Errore 429 (Rate Limit)
**Soluzione:** Cambia modello a `gemini-2.5-flash` o riduci `MAX_CHUNKS_FOR_GENERATION`

### Errore 503 (Model Overloaded)
**Soluzione:** Transiente, riprova dopo qualche secondo. Circuit breaker gestisce automaticamente.

### Troppe Fonti Non Pertinenti
**Soluzione:** Aumenta `MIN_RELEVANCE_SCORE` a 0.4-0.5 in `.env`

### Risposta Troppo Generica
**Soluzione:** Riduci `MAX_CHUNKS_FOR_GENERATION` a 10 e aumenta `MIN_RELEVANCE_SCORE`

### "Recupera sempre 17 chunks invece di 25"
**Causa:** Limite interno API Google o pochi chunks disponibili
**Soluzione:** Verifica numero totale chunks nel documento via modal

### Documento in PROCESSING
**Soluzione:** Attendi qualche minuto, l'elaborazione richiede tempo

### Server non parte
**Soluzione:** Verifica `.env` con `GEMINI_API_KEY` e `FILE_SEARCH_STORE_NAME`

### Errore 500 su /api/documents
- **Causa**: Store name non valido o store inesistente
- **Soluzione**: Esegui `python backend/create_store.py` e aggiorna `.env`

📖 **Guida completa**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 🔍 Dettagli Tecnici

### Stati Documento

- **STATE_PENDING**: Documento in elaborazione (generazione embeddings)
- **STATE_ACTIVE**: Documento pronto per query di ricerca
- **STATE_FAILED**: Errore durante elaborazione

### Long-Running Operations

L'upload dei documenti è asincrono:

1. L'API restituisce immediatamente un oggetto `Operation`
2. Il frontend effettua polling ogni 3 secondi
3. Quando `done: true`, l'operazione è completata
4. La lista documenti viene aggiornata automaticamente

### Gestione Errori

- Validazione input lato client e server
- Logging dettagliato delle operazioni
- Messaggi di errore user-friendly
- Retry automatico per operazioni in polling

## 🛡️ Sicurezza

⚠️ **IMPORTANTE**: Questo è un sistema amministrativo. In produzione:

1. Implementa autenticazione (OAuth, JWT, ecc.)
2. Usa HTTPS per tutte le comunicazioni
3. Non esporre l'API Key nel frontend
4. Implementa rate limiting
5. Valida e sanitizza tutti gli input
6. Usa CORS in modo restrittivo

## 🐛 Script di Utility

### Test Connessione API

```bash
cd backend
python test_api.py          # Verifica API Key e Store
python test_upload.py       # Test upload documento
python test_chunks.py       # Test retrieval chunks
python test_list_documents.py  # Test lista documenti
```

### Crea Nuovo File Search Store

```bash
cd backend
python create_store.py
```

### Verifica Setup

```bash
python setup.py
```

### Visualizza Configurazione Corrente

```bash
curl http://localhost:5000/api/config
```

## 📊 Monitoring e Logging

### Log Dettagliati

Il server registra:
- **Chunk Stats**: "Chunk recuperati: 25, Score >= 0.3: 17, Usati: 15"
- **Operazioni Upload**: Progress e stato elaborazione
- **Circuit Breaker**: Stato (CLOSED/OPEN/HALF_OPEN)
- **Errori API**: Dettagli completi per debugging

### Frontend Console

Apri DevTools (F12) per vedere:
- ✅ "Recuperati X chunk rilevanti"
- ⚙️ Configurazione caricata (chunk_size, overlap, etc.)
- 📊 Score rilevanza per ogni chunk
- ❌ Errori dettagliati con stack trace

## 📚 Documentazione

### Setup e Installazione
- **[setup/INSTALL.md](setup/INSTALL.md)** - Guida installazione completa con checklist
- **[setup/CHECKLIST.md](setup/CHECKLIST.md)** - Checklist verifica setup
- **[setup/README.md](setup/README.md)** - Guida script setup e avvio

### Documentazione Tecnica
- **[docs/LOGICA_FILTRAGGIO_CHUNKS.md](docs/LOGICA_FILTRAGGIO_CHUNKS.md)** - Architettura RAG e filtraggio
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Risoluzione problemi comuni
- **[docs/IMPROVEMENTS_LOG.md](docs/IMPROVEMENTS_LOG.md)** - Cronologia miglioramenti
- **[docs/README.md](docs/README.md)** - Indice completo documentazione

### Test
- **[backend/tests/README.md](backend/tests/README.md)** - Guida esecuzione test suite

### Risorse Esterne

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [File Search API Reference](https://ai.google.dev/api/rest/v1beta/fileSearchStores)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [RAG Best Practices](https://www.anthropic.com/index/contextual-retrieval)

## 🚀 Changelog

### v2.0.0 (2025-11-11)

**🎯 RAG Ottimizzato**
- ✨ Filtro intelligente per relevance score (MIN_RELEVANCE_SCORE)
- ✨ Limite configurabile chunks per generazione (MAX_CHUNKS_FOR_GENERATION)
- ✨ Prompt engineering migliorato per risposte sintetizzate
- ✨ Riduzione fonti non pertinenti nella visualizzazione

**📄 Gestione Documenti**
- ✨ Metadato riservato `document_location` per percorsi file
- ✨ Pulsante "Apri Documento" per apertura file originali
- ✨ Modal visualizzazione chunks con score rilevanza
- ✨ Chunking configurabile (size + overlap %)

**⚙️ Configurazione**
- ✨ RESULTS_COUNT configurabile via .env (default 25)
- ✨ Esposizione parametri via /api/config
- ✨ Documentazione completa logica filtraggio

**🔧 Miglioramenti Tecnici**
- 🐛 Fix visualizzazione fonti (solo documenti usati)
- 🐛 Circuit breaker per gestione rate limit
- 📊 Logging dettagliato con statistiche chunks
- 🎨 UI migliorata con icone e feedback visivo

### v1.0.0 (2024)
- 🎉 Release iniziale
- 📤 Upload documenti con metadati custom
- 💬 Chatbot RAG con Gemini
- 🔍 Ricerca semantica multi-documento

## 👨‍💻 Autore

**Attilio**
- GitHub: [@Attilio81](https://github.com/Attilio81)
- Repository: [GoogleFileSearch](https://github.com/Attilio81/GoogleFileSearch)

## 🤝 Contributi

I contributi sono benvenuti! Per favore:
1. Fork il repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

MIT License - Vedi [LICENSE](LICENSE) per dettagli

---

**Made with ❤️ using Google AI, Flask and RAG optimization**

⭐ Se ti piace questo progetto, lascia una stella su GitHub!
