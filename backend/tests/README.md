# Test Suite

## Esecuzione Test

```bash
# Tutti i test
pytest backend/tests/ -v

# Test specifico
pytest backend/tests/test_rag.py::test_query_validation_xss -v

# Con coverage
pytest backend/tests/ --cov=backend --cov-report=html
```

## Test Implementati

### Validazione Query
- ✅ Blocca XSS (`<script>`)
- ✅ Blocca SQL injection
- ✅ Blocca query vuote
- ✅ Blocca query troppo lunghe (>10000 caratteri)
- ✅ Accetta query valide

### Endpoint
- ✅ `/api/config` - Configurazione
- ✅ `/api/documents` - Lista documenti
- ✅ `/api/chat/query` - Query documenti
- ✅ `/api/chat/generate` - Generazione risposta

### Rate Limiting
- ✅ 30 richieste / minuto per IP
- ✅ Risponde 429 Too Many Requests

### Cache
- ✅ Cache query con TTL 5 minuti
- ✅ Cache hit logs
- ✅ Auto-expiration

## Configurazione Test

Le configurazioni per test sono definite in `.env`:
```properties
QUERY_CACHE_TTL=300  # 5 minuti
RATE_LIMIT_MAX=30    # richieste/minuto
RATE_LIMIT_WINDOW=60 # 1 minuto
```
