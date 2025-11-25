# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **RAG (Retrieval-Augmented Generation) system** built with Google's Gemini File Search API and Gemini AI. The system enables document management with semantic search and AI-powered question answering based on uploaded documents.

**Key Technologies:**
- Backend: Flask 3.0, Python 3.8+
- Frontend: Vanilla JavaScript (no framework)
- AI: Google Gemini API (File Search + Generation)
- Architecture: Two-phase RAG (Retrieval → Generation)

## Development Commands

### Start the Application

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Start Flask server (from backend directory)
cd backend
python app.py
```

Server runs on `http://localhost:5000`

### Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate and install
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Testing Utilities

```bash
cd backend

# Test API connectivity and configuration
python test_api.py

# Test document upload flow
python test_upload.py

# Test chunk retrieval with scores
python test_chunks.py

# Test query with relevance scores
python test_query_scores.py

# List all documents in store
python test_list_documents.py

# Create a new File Search Store
python create_store.py
```

### Configuration

Copy `.env.example` to `.env` and configure:
- `GEMINI_API_KEY`: Required - Get from https://makersuite.google.com/app/apikey
- `FILE_SEARCH_STORE_NAME`: Required - Format: `fileSearchStores/store-id`
- RAG parameters: `RESULTS_COUNT`, `MIN_RELEVANCE_SCORE`, `MAX_CHUNKS_FOR_GENERATION`
- Chunking: `CHUNK_SIZE` (1-512 tokens), `CHUNK_OVERLAP_PERCENT` (0-50%)

## Architecture

### RAG Pipeline (Two-Phase)

The system implements an optimized two-phase RAG approach:

**Phase 1: Retrieval** (`/api/chat/query`)
- Semantic search via Google File Search API
- Retrieves `RESULTS_COUNT` chunks (default: 25)
- Returns chunks with `chunkRelevanceScore` (0.0-1.0)

**Phase 2: Generation** (`/api/chat/generate` or `/api/chat/generate-stream`)
- Filters chunks by `MIN_RELEVANCE_SCORE` (default: 0.3)
- Selects top `MAX_CHUNKS_FOR_GENERATION` chunks (default: 15)
- Sends filtered context to Gemini for answer synthesis
- Streaming endpoint uses Server-Sent Events (SSE)

**Key Insight:** The filtering logic reduces noise by only using high-relevance chunks, improving answer quality and reducing token usage.

### Backend Structure (`backend/app.py`)

**Core Components:**
1. **CircuitBreaker class**: Handles Gemini API rate limiting (429 errors)
   - States: CLOSED, OPEN, HALF_OPEN
   - Auto-recovery after timeout
   - Located at lines 60-102

2. **Validation Functions** (lines 110-183):
   - `validate_query_text()`: XSS prevention, length checks
   - `validate_mime_type()`: File type validation
   - `validate_metadata()`: Custom metadata validation

3. **Document Management**:
   - Upload: `/api/documents/upload` (Long-Running Operation with polling)
   - List: `/api/documents` (paginated, max 20 per page)
   - Delete: `/api/documents/{name}` (with `force=true` to delete chunks)
   - Chunks: `/api/documents/{name}/chunks` (semantic search within document)

4. **RAG Endpoints**:
   - Query: `/api/chat/query` (retrieval phase)
   - Generate: `/api/chat/generate` (generation phase, synchronous)
   - Generate-stream: `/api/chat/generate-stream` (generation with SSE)

5. **Frontend Routes**:
   - `/` - Admin panel (document management)
   - `/chat` - Chatbot interface
   - `/chunks` - Document chunks viewer

### Frontend Structure

**Templates** (`frontend/templates/`):
- `index.html` - Admin UI for document upload/management
- `chat.html` - Chat interface with streaming support
- `chunks.html` - Chunk visualization with search

**JavaScript** (`frontend/static/js/`):
- `app.js` - Admin panel logic (upload, delete, polling operations)
- `chat.js` - Chat UI with SSE streaming, source citation
- `chunks.js` - Chunk viewer with semantic search

**CSS** (`frontend/static/css/`):
- `styles.css` - Admin panel styling
- `chat.css` - Chat interface styling

### Key Implementation Details

**Document Upload Flow:**
1. File validated (MIME type, size)
2. Saved temporarily to disk (not memory - important for large files)
3. Multipart upload to Google API with metadata
4. Returns Long-Running Operation (LRO)
5. Frontend polls `/api/operations/{name}` every 3s
6. Updates document list when `done: true`

**Chunking Configuration:**
- API limit: 1-512 tokens per chunk
- Overlap calculated: `chunk_size * CHUNK_OVERLAP_PERCENT / 100`
- Max overlap: 100 tokens (API constraint)
- Config sent in `chunkingConfig.whiteSpaceConfig`

**Circuit Breaker Pattern:**
- Prevents cascading failures on 429 errors
- Global instance: `gemini_circuit_breaker`
- Call `record_success()` or `record_failure()` after API calls
- Check `call_allowed()` before requests

**Metadata Handling:**
- Custom metadata: key-value pairs (max 50)
- Reserved key: `document_location` (for file path linking)
- Frontend displays "Apri Documento" button if `document_location` exists

**Security Validations:**
- XSS prevention in query text (checks for `<script`, `javascript:`, etc.)
- MIME type whitelist enforcement
- Metadata key/value sanitization
- Secure filename handling with `werkzeug.utils.secure_filename`

## Important Patterns

### Error Handling

Always use try-except with detailed logging:
```python
try:
    # API call
    response = requests.get(url, headers=headers)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"Detailed error: {str(e)}")
    return jsonify({'success': False, 'error': 'User-friendly message'}), 500
```

### API Headers

Use `get_headers()` function for all API requests:
```python
def get_headers():
    return {'x-goog-api-key': GEMINI_API_KEY}
```

### Logging Format

Use structured logging with context:
```python
logger.info(f"Chunk stats - Retrieved: {total}, Score >= {threshold}: {filtered}, Used: {final}")
```

### Frontend API Calls

Always check `success` field in JSON responses:
```javascript
const response = await fetch('/api/endpoint', {...});
const data = await response.json();
if (!data.success) {
    showError(data.error);
    return;
}
// Process data.result
```

## Common Workflows

### Adding a New RAG Configuration Parameter

1. Add to `.env.example` with documentation
2. Load in `backend/app.py` with `os.getenv()` and default
3. Add to `/api/config` endpoint return value
4. Update frontend to fetch and display in UI
5. Document in README.md parameter table

### Modifying Chunk Filtering Logic

The filtering happens in `/api/chat/generate` (lines 629-639):
1. Filter by `MIN_RELEVANCE_SCORE`
2. Take top `MAX_CHUNKS_FOR_GENERATION`
3. Log statistics for debugging
4. Use filtered chunks for context building

### Adding New Document Metadata

1. Add input fields in `index.html` upload form
2. Collect in `app.js` FormData
3. Validate in `validate_metadata()` function
4. Pass to API in `customMetadata` array format:
   ```python
   {'key': 'metadata_name', 'stringValue': 'value'}
   ```

### Testing a New Feature

1. Write test script in `backend/test_*.py` format
2. Use `load_dotenv('../.env')` to load config
3. Make direct API calls with error handling
4. Print clear success/failure messages with emojis (✅/❌)

## API Constraints & Limits

- **Chunk size**: 1-512 tokens (API enforced)
- **Chunk overlap**: Max 100 tokens
- **Documents per page**: Max 20 (Google API limit)
- **Max file size**: 100MB (configurable in `app.config`)
- **Custom metadata**: Max 50 key-value pairs
- **Query length**: Max 2000 characters (app validation)
- **Rate limits**: Handled by CircuitBreaker

## Troubleshooting

**429 Rate Limit Errors:**
- Circuit breaker automatically handles with retries
- Switch to `gemini-2.5-flash` (faster model)
- Reduce `MAX_CHUNKS_FOR_GENERATION`

**503 Model Overloaded:**
- Transient error, circuit breaker manages recovery
- Check Gemini API status page

**Upload stays in PROCESSING:**
- Normal for large files (can take minutes)
- Check operation status with `/api/operations/{name}`
- Google API processes embeddings asynchronously

**Store not found (500 on /api/documents):**
- Verify `FILE_SEARCH_STORE_NAME` in `.env`
- Run `python backend/create_store.py` to create new store

## Additional Documentation

- `README.md` - Full user documentation with setup guide
- `LOGICA_FILTRAGGIO_CHUNKS.md` - Detailed RAG filtering explanation
- `IMPROVEMENTS_LOG.md` - Changelog of optimizations
- `TROUBLESHOOTING.md` - Extended troubleshooting guide
