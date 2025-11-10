# 🤖 Google File Search RAG - Sistema di Gestione Documenti e Chatbot

Sistema completo per la gestione di documenti e chatbot basato su **Google File Search API** e **Gemini AI**. Implementa un sistema RAG (Retrieval-Augmented Generation) per interrogare documenti con intelligenza artificiale.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![Google AI](https://img.shields.io/badge/Google%20AI-Gemini-orange)

## 🎯 Funzionalità

### 🗂️ Gestione Documenti

- **📤 Upload Documenti**: Carica file nel File Search Store con gestione asincrona (Long-Running Operations)
- **📋 Visualizzazione**: Lista completa dei documenti con stato, dimensione e metadati
- **🔍 Monitoraggio**: Tracking in tempo reale delle operazioni di upload in corso
- **🗑️ Eliminazione**: Rimozione sicura dei documenti con conferma (elimina anche i chunk associati)
- **⚙️ Metadati Custom**: Supporto per metadati personalizzati durante l'upload
- **Formati supportati**: PDF, TXT, DOC, DOCX, XLS, XLSX, CSV, JSON, HTML, MD

### 💬 Chatbot RAG

- **🔍 Retrieval semantico** sui documenti caricati
- **🤖 Generazione risposte** con Gemini AI
- **💭 Conversazioni multi-turn** con memoria del contesto
- **📚 Visualizzazione fonti** dei documenti utilizzati
- **⚙️ Selezione modello** Gemini configurabile
- **🔄 Retry automatico** su errori di rate limit
- **💾 Persistenza cronologia** con salvataggio automatico in localStorage
- **📱 Design responsive** per mobile e desktop

### 📦 Visualizzatore Chunks

- **🔬 Analisi chunks**: Visualizza come i documenti vengono suddivisi in chunks
- **🔍 Query semantica**: Cerca chunks specifici usando parole chiave
- **➕ Espandi/Riduci**: Naviga facilmente tra i chunks
- **🔦 Evidenziazione testo**: Ricerca full-text all'interno dei chunks
- **📊 Statistiche**: Visualizza informazioni su numero e dimensione dei chunks

## 🏗️ Architettura

```
User Query → Retrieval (File Search API) → Generation (Gemini) → Response
             ↓ Semantic Search              ↓ Context + Prompt
             Relevant Chunks                 AI-Generated Answer
```

### Struttura Progetto

```
GoogleFileSearch/
├── backend/
│   ├── app.py                    # Flask app principale
│   ├── create_store.py           # Crea File Search Store
│   ├── test_api.py               # Test connessione API
│   └── test_chunks.py            # Test visualizzazione chunks
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── styles.css        # Stili admin
│   │   │   ├── chat.css          # Stili chatbot
│   │   │   └── chunks.css        # Stili visualizzatore chunks
│   │   └── js/
│   │       ├── app.js            # Logic admin
│   │       ├── chat.js           # Logic chatbot
│   │       └── chunks.js         # Logic visualizzatore chunks
│   └── templates/
│       ├── index.html            # Admin UI
│       ├── chat.html             # Chat UI
│       └── chunks.html           # Visualizzatore chunks
├── .env                          # Config (da creare)
├── .env.example                  # Template configurazione
├── requirements.txt              # Dipendenze Python
├── IMPROVEMENTS_LOG.md           # Log miglioramenti produzione
└── README.md                     # Questa documentazione
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
GEMINI_API_KEY=la_tua_api_key
FILE_SEARCH_STORE_NAME=fileSearchStores/il-tuo-store-id
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
- **Visualizzatore Chunks:** http://localhost:5000/chunks

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
4. La cronologia viene salvata automaticamente e ripristinata al refresh

### Visualizzazione Chunks

1. Accedi al visualizzatore chunks (http://localhost:5000/chunks)
2. Seleziona un documento dalla lista a tendina
3. (Opzionale) Inserisci una query di ricerca o lascia vuoto per vedere tutti i chunks
4. Clicca "🔍 Carica Chunks"
5. Utilizza i controlli per:
   - **Espandi/Riduci tutto**: Visualizza o nascondi tutti i chunks contemporaneamente
   - **Ricerca testo**: Cerca all'interno del contenuto dei chunks (evidenziazione in tempo reale)
   - **Statistiche**: Visualizza informazioni sul documento e i suoi chunks

## 🔌 API Endpoints

### Configurazione

- `GET /api/config` - Restituisce la configurazione corrente (senza API key)

### Gestione Documenti

- `GET /api/documents` - Lista documenti con paginazione
- `POST /api/documents/upload` - Upload documento (Long-Running Operation)
- `DELETE /api/documents/{name}` - Elimina documento
- `GET /api/operations/{name}` - Stato operazione di upload
- `POST /api/documents/{name}/chunks` - Recupera chunks con query semantica

### Chatbot RAG

- `POST /api/chat/query` - Retrieval (cerca chunk rilevanti)
- `POST /api/chat/generate` - Generation (genera risposta)
- `POST /api/chat/generate-stream` - Generation con streaming SSE (disponibile ma non integrato in UI)

### Interfacce

- `GET /` - Admin panel
- `GET /chat` - Chatbot interface
- `GET /chunks` - Visualizzatore chunks documenti

## 🤖 Modelli Gemini Supportati

| Modello | Velocità | Rate Limit | Consigliato |
|---------|----------|------------|-------------|
| `gemini-2.5-flash-lite` | Veloce | Alto | ✅ Default |
| `gemini-1.5-flash-latest` | Veloce | Alto | ✅ Alternativa |
| `gemini-1.5-pro-latest` | Medio | Medio | Per query complesse |
| `gemini-2.0-flash-exp` | Variabile | Basso | ⚠️ Solo test |

## 🔧 Troubleshooting

### Errore 429 (Rate Limit)
**Soluzione:** Cambia modello a `gemini-2.5-flash-lite` nelle impostazioni del chatbot

### Errore 404 sul modello
**Soluzione:** Usa solo modelli supportati (vedi tabella sopra)

### Documento in PROCESSING
**Soluzione:** Attendi qualche minuto, l'elaborazione richiede tempo

### Server non parte
**Soluzione:** Verifica `.env` con `GEMINI_API_KEY` e `FILE_SEARCH_STORE_NAME`

### Errore 500 su /api/documents
- **Causa**: Store name non valido o store inesistente
- **Soluzione**: Esegui `python backend/create_store.py` e aggiorna `.env`

### Operazione bloccata su STATE_PENDING
- Normale per file grandi (può richiedere minuti)
- Controlla i log del server per errori
- Verifica lo stato tramite API Google direttamente

## ⚙️ Funzionalità Avanzate

### 🛡️ Circuit Breaker per Rate Limits

Il sistema implementa un **Circuit Breaker** intelligente per gestire i rate limits dell'API Gemini:

- **Stati**: CLOSED (normale), OPEN (blocco dopo fallimenti), HALF_OPEN (test ripristino)
- **Threshold**: 5 fallimenti consecutivi → apertura circuito
- **Timeout**: 60 secondi di attesa prima di riprovare
- **Reset automatico**: Su successo, il circuito si chiude
- **Risposta**: HTTP 503 quando il circuito è aperto

### 🔒 Input Validation e Sicurezza

Protezione completa contro attacchi comuni:

**Validazione Query:**
- Lunghezza massima: 2000 caratteri
- Rilevamento pattern XSS: `<script>`, `javascript:`, `onerror=`
- Blocco SQL injection: `'; DROP`, `' OR '1'='1`

**Validazione MIME Type:**
- Whitelist rigorosa di tipi consentiti
- Supporto: PDF, DOC, DOCX, TXT, RTF, XLS, XLSX, CSV, PPT, PPTX, JSON, XML, HTML

**Validazione Metadati:**
- Massimo 50 coppie chiave-valore
- Lunghezza chiavi: max 100 caratteri
- Lunghezza valori: max 500 caratteri
- Protezione da injection nei metadati

### 💾 File Storage Ottimizzato

Gestione robusta dei file upload:

- **Storage su disco**: Uso di directory temporanea del sistema operativo
- **Nessun limite memoria**: File non caricati in RAM
- **Cleanup garantito**: Rimozione automatica file temporanei con `finally` block
- **Gestione errori**: Log dettagliato di tutte le operazioni

### 📡 Streaming Responses (Disponibile)

Endpoint per risposte in tempo reale:

- **Endpoint**: `/api/chat/generate-stream`
- **Protocollo**: Server-Sent Events (SSE)
- **MIME Type**: `text/event-stream`
- **Validazione**: Identica all'endpoint standard
- **Circuit Breaker**: Completamente integrato
- **Stato**: Backend pronto, frontend da integrare

### 📄 Pagination

Navigazione efficiente tra documenti:

- **Page Size**: Default 20, massimo 100 documenti per pagina
- **Page Token**: Gestione automatica della paginazione
- **UI**: Controlli "Pagina Successiva" con visibilità intelligente
- **Performance**: Caricamento progressivo per grandi archivi

### 💭 Chat History Persistence

Salvataggio automatico delle conversazioni:

- **Storage**: localStorage del browser
- **Limite**: Ultimi 20 messaggi (10 interazioni)
- **Session ID**: Univoco per futura gestione multi-sessione
- **Auto-restore**: Ripristino cronologia al caricamento pagina
- **Controlli**: Pulsante "Cancella Cronologia" con conferma

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
python test_api.py
```

### Visualizza Chunks da CLI

Strumento interattivo per esplorare chunks dei documenti:

```bash
cd backend
python test_chunks.py
```

Lo script ti permette di:
- Selezionare un documento dalla lista
- Visualizzare tutti i chunks con statistiche
- Vedere il contenuto di ogni chunk
- Salvare i dati completi in formato JSON

### Crea Nuovo File Search Store

```bash
cd backend
python create_store.py
```

### Verifica Setup

```bash
python setup.py
```

## 📚 Risorse

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [File Search API Reference](https://ai.google.dev/api/rest/v1beta/fileSearchStores)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [IMPROVEMENTS_LOG.md](IMPROVEMENTS_LOG.md) - Documentazione dettagliata dei miglioramenti production-ready

## 👨‍💻 Autore

**Attilio**
- GitHub: [@Attilio81](https://github.com/Attilio81)
- Repository: [GoogleFileSearch](https://github.com/Attilio81/GoogleFileSearch)

## 📄 Licenza

MIT License - Vedi [LICENSE](LICENSE) per dettagli

---

**Made with ❤️ using Google AI and Flask**
