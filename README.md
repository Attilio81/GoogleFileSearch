# 🤖 Google File Search RAG - Sistema di Gestione Documenti e Chatbot# Gestione Documenti - Google RAG File Search API



Sistema completo per la gestione di documenti e chatbot basato su **Google File Search API** e **Gemini AI**. Implementa un sistema RAG (Retrieval-Augmented Generation) per interrogare documenti con intelligenza artificiale.Sistema di backend amministrativo per la gestione di documenti utilizzando le **Google Gemini File Search API** (v1beta) per implementare un sistema RAG (Retrieval-Augmented Generation).



![Python](https://img.shields.io/badge/Python-3.8+-blue)## 🎯 Funzionalità

![Flask](https://img.shields.io/badge/Flask-3.0+-green)

![Google AI](https://img.shields.io/badge/Google%20AI-Gemini-orange)- **📤 Upload Documenti**: Carica file nel File Search Store con gestione asincrona (Long-Running Operations)

- **📋 Visualizzazione**: Lista completa dei documenti con stato, dimensione e metadati

## ✨ Caratteristiche- **🔍 Monitoraggio**: Tracking in tempo reale delle operazioni di upload in corso

- **🗑️ Eliminazione**: Rimozione sicura dei documenti con conferma (elimina anche i chunk associati)

### 🗂️ Gestione Documenti- **⚙️ Metadati Custom**: Supporto per metadati personalizzati durante l'upload

- ✅ **Upload documenti** (PDF, TXT, DOC, DOCX, XLS, XLSX, CSV, JSON, HTML, MD)

- ✅ **Gestione metadati** personalizzati## 🏗️ Architettura

- ✅ **Monitoraggio stato** documenti (PROCESSING, ACTIVE, FAILED)

- ✅ **Eliminazione documenti** con conferma```

- ✅ **Visualizzazione dettagli** completiGestione Documenti GoogleSearch/

├── backend/

### 💬 Chatbot RAG│   └── app.py              # Server Flask con API endpoints

- ✅ **Retrieval semantico** sui documenti caricati├── frontend/

- ✅ **Generazione risposte** con Gemini AI│   ├── templates/

- ✅ **Conversazioni multi-turn** con memoria del contesto│   │   └── index.html      # Interfaccia amministrativa

- ✅ **Visualizzazione fonti** dei documenti utilizzati│   └── static/

- ✅ **Selezione modello** Gemini configurabile│       ├── css/

- ✅ **Retry automatico** su errori di rate limit│       │   └── styles.css  # Stili personalizzati

- ✅ **Design responsive** per mobile e desktop│       └── js/

│           └── app.js      # Logica frontend e gestione API

## 🚀 Installazione Rapida├── .env                     # Configurazione (da creare)

├── .env.example            # Template configurazione

```bash├── requirements.txt        # Dipendenze Python

# 1. Clona il repository└── README.md              # Questa documentazione

git clone https://github.com/Attilio81/GoogleFileSearch.git```

cd GoogleFileSearch

## 🚀 Setup e Installazione

# 2. Crea virtual environment

python -m venv venv### 1. Prerequisiti

venv\Scripts\activate  # Windows

# source venv/bin/activate  # Linux/Mac- Python 3.8 o superiore

- Account Google Cloud con accesso alle Gemini API

# 3. Installa dipendenze- API Key di Google Gemini

pip install -r requirements.txt- File Search Store già creato



# 4. Configura .env### 2. Clona/Scarica il Progetto

echo GEMINI_API_KEY=your_api_key_here > .env

echo FILE_SEARCH_STORE_NAME=fileSearchStores/your-store-name >> .env```bash

cd "c:\Progetti Pilota\Gestione Documenti GoogleSearch"

# 5. Avvia il server```

cd backend

python app.py### 3. Crea Ambiente Virtuale

```

```powershell

Accedi a:python -m venv venv

- **Admin Panel:** http://localhost:5000.\venv\Scripts\Activate.ps1

- **Chatbot:** http://localhost:5000/chat```



## 📋 Requisiti### 4. Installa Dipendenze



- **Python 3.8+**```powershell

- **Chiave API Google AI Studio** ([Ottienila qui](https://aistudio.google.com/apikey))pip install -r requirements.txt

- **File Search Store** ([Crealo con `backend/create_store.py`](backend/create_store.py))```



## 🏗️ Architettura RAG### 5. Configura Variabili d'Ambiente



```Crea un file `.env` copiando `.env.example`:

User Query → Retrieval (File Search API) → Generation (Gemini) → Response

             ↓ Semantic Search              ↓ Context + Prompt```powershell

             Relevant Chunks                 AI-Generated AnswerCopy-Item .env.example .env

``````



## 📁 Struttura ProgettoModifica `.env` con i tuoi dati:



``````env

GoogleFileSearch/GEMINI_API_KEY=la_tua_api_key

├── backend/FILE_SEARCH_STORE_NAME=fileSearchStores/il-tuo-store-id

│   ├── app.py                    # Flask app principale```

│   ├── create_store.py           # Crea File Search Store

│   └── test_*.py                 # Script di test#### Come ottenere l'API Key:

├── frontend/

│   ├── static/1. Vai su https://makersuite.google.com/app/apikey

│   │   ├── css/2. Crea un nuovo progetto o seleziona uno esistente

│   │   │   ├── styles.css       # Stili admin3. Genera una nuova API Key

│   │   │   └── chat.css         # Stili chatbot4. Copia la chiave nel file `.env`

│   │   └── js/

│   │       ├── app.js           # Logic admin#### Come creare un File Search Store:

│   │       └── chat.js          # Logic chatbot

│   └── templates/Puoi creare un File Search Store tramite API REST:

│       ├── index.html           # Admin UI

│       └── chat.html            # Chat UI```bash

├── .env                         # Config (da creare)curl -X POST "https://generativelanguage.googleapis.com/v1beta/fileSearchStores" \

├── requirements.txt             # Dipendenze  -H "x-goog-api-key: YOUR_API_KEY" \

└── README.md                    # Questa guida  -H "Content-Type: application/json" \

```  -d '{

    "displayName": "My RAG Store"

## 🔌 API Endpoints Principali  }'

```

### Gestione Documenti

- `GET /api/documents` - Lista documentiLa risposta conterrà il nome della risorsa (es: `fileSearchStores/abc123`) da usare in `.env`.

- `POST /api/documents/upload` - Upload documento

- `DELETE /api/documents/{name}` - Elimina documento### 6. Avvia il Server

- `GET /api/operations/{name}` - Stato operazione

```powershell

### Chatbot RAGcd backend

- `POST /api/chat/query` - Retrieval (cerca chunk rilevanti)python app.py

- `POST /api/chat/generate` - Generation (genera risposta)```



### InterfacceIl server sarà disponibile su: http://localhost:5000

- `GET /` - Admin panel

- `GET /chat` - Chatbot interface### 7. Accedi all'Interfaccia



## 🎯 Come Usare il ChatbotApri il browser e vai su: http://localhost:5000



1. **Carica documenti** tramite Admin Panel (http://localhost:5000)## 📖 Utilizzo

2. **Accedi al chatbot** (http://localhost:5000/chat)

3. **Fai una domanda** - Il sistema:### Caricamento Documenti

   - Cerca nei documenti i passaggi rilevanti (Retrieval)

   - Genera una risposta contestualizzata (Generation)1. Clicca su "Seleziona File" e scegli il documento

   - Mostra le fonti utilizzate2. (Opzionale) Specifica un nome visualizzazione custom

3. (Opzionale) Aggiungi metadati personalizzati

### Modelli Gemini Supportati4. Clicca "Carica Documento"

5. L'operazione verrà tracciata nella sezione "Operazioni in Corso"

| Modello | Velocità | Rate Limit | Consigliato |

|---------|----------|------------|-------------|### Monitoraggio Stato

| `gemini-2.5-flash-lite` | Veloce | Alto | ✅ Default |

| `gemini-1.5-flash-latest` | Veloce | Alto | ✅ Alternativa |- La tabella mostra tutti i documenti con il loro stato:

| `gemini-1.5-pro-latest` | Medio | Medio | Per query complesse |  - **✅ Attivo**: Documento pronto per la ricerca

| `gemini-2.0-flash-exp` | Variabile | Basso | ⚠️ Solo test |  - **⏳ In elaborazione**: Upload completato, elaborazione embedding in corso

  - **❌ Fallito**: Errore durante l'elaborazione

## 🔧 Troubleshooting

### Eliminazione Documenti

### Errore 429 (Rate Limit)

**Soluzione:** Cambia modello a `gemini-2.5-flash-lite` nelle impostazioni del chatbot1. Clicca sul pulsante "🗑️ Elimina" nella riga del documento

2. Conferma l'eliminazione nel modal

### Errore 404 sul modello3. Il documento e tutti i chunk associati verranno eliminati

**Soluzione:** Usa solo modelli supportati (vedi tabella sopra)

## 🔧 API Endpoints

### Documento in PROCESSING

**Soluzione:** Attendi qualche minuto, l'elaborazione richiede tempo### GET /api/config

Restituisce la configurazione corrente (senza API key)

### Server non parte

**Soluzione:** Verifica `.env` con `GEMINI_API_KEY` e `FILE_SEARCH_STORE_NAME`### GET /api/documents

Elenca tutti i documenti nel File Search Store

## 📚 Documentazione Completa

**Query Parameters:**

Per la documentazione dettagliata di API, configurazione e troubleshooting, consulta:- `pageSize`: Numero di risultati per pagina (default: 100)

- [Documentazione Google File Search](https://ai.google.dev/api/file-search)- `pageToken`: Token per paginazione

- [Documentazione Gemini API](https://ai.google.dev/docs)

**Response:**

## 👨‍💻 Autore```json

{

**Attilio**    "success": true,

GitHub: [@Attilio81](https://github.com/Attilio81)    "documents": [

Repository: [GoogleFileSearch](https://github.com/Attilio81/GoogleFileSearch)    {

      "name": "fileSearchStores/xxx/documents/yyy",

## 📄 Licenza      "displayName": "Nome documento",

      "sizeBytes": 12345,

MIT License - Vedi [LICENSE](LICENSE) per dettagli      "createTime": "2024-01-01T12:00:00Z",

      "state": "STATE_ACTIVE"

---    }

  ],

**Made with ❤️ using Google AI and Flask**  "nextPageToken": "..."

}
```

### POST /api/documents/upload
Carica un nuovo documento (Long-Running Operation)

**Body (multipart/form-data):**
- `file`: File da caricare (required)
- `displayName`: Nome visualizzazione (optional)
- `mimeType`: Tipo MIME (optional, auto-detect)
- `metadataKeys[]`: Array di chiavi metadati (optional)
- `metadataValues[]`: Array di valori metadati (optional)

**Response:**
```json
{
  "success": true,
  "operationName": "fileSearchStores/.../upload/operations/...",
  "operation": { ... },
  "message": "Upload avviato con successo"
}
```

### GET /api/operations/{operation_name}
Controlla lo stato di un'operazione di upload

**Response:**
```json
{
  "success": true,
  "done": true,
  "operation": { ... },
  "document": { ... }
}
```

### DELETE /api/documents/{document_name}
Elimina un documento e tutti i chunk associati

**Query Parameters:**
- `force=true` (automatico): Elimina anche i chunk

**Response:**
```json
{
  "success": true,
  "message": "Documento eliminato con successo"
}
```

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

## 🐛 Debugging e Troubleshooting

### Attiva logging dettagliato

Il server Flask registra automaticamente:
- Tutte le richieste API
- Errori e eccezioni
- Stati delle operazioni

I log vengono stampati nella console del server.

### Script di Utility

**Test Connessione API:**
```powershell
cd backend
python test_api.py
```

**Crea Nuovo File Search Store:**
```powershell
cd backend
python create_store.py
```

**Verifica Setup:**
```powershell
python setup.py
```

### Problemi Comuni

**❌ Errore 500 su /api/documents**
- **Causa**: Store name non valido o store inesistente
- **Soluzione**: Esegui `python backend/create_store.py` e aggiorna `.env`

**❌ Errore: GEMINI_API_KEY non configurata**
- Verifica che il file `.env` esista
- Controlla che la chiave API sia corretta

**⏳ Operazione bloccata su STATE_PENDING**
- Normale per file grandi (può richiedere minuti)
- Controlla i log del server per errori
- Verifica lo stato tramite API Google direttamente

**📋 Guida completa:** Vedi [TROUBLESHOOTING.md](TROUBLESHOOTING.md) per tutti i problemi e soluzioni

## 📚 Risorse

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [File Search API Reference](https://ai.google.dev/api/rest/v1beta/fileSearchStores)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 📝 License

Questo progetto è fornito "as-is" per scopi educativi e di sviluppo.

## 🤝 Contributi

Per miglioramenti o bug report, crea un issue o pull request.

---

**Sviluppato con ❤️ per la gestione intelligente di documenti RAG**
